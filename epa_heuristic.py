"""Standalone Football Dice expected-points heuristic.

All numeric play outcomes, field-goal odds and baseline expected-points
coefficients are illustrative until calibrated to the actual game rules.

Field position: yards from offense's own goal line (0..100).
Positive utility is good for the player currently on offense.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Callable, Mapping, Sequence


@dataclass(frozen=True)
class GameState:
    score_for: int
    score_against: int
    down: int
    yard_line: int
    yards_to_go: int
    timeouts: int = 3
    blitzes: int = 5
    audibles: int = 5
    possessions_left: int = 3

    def __post_init__(self):
        if not 1 <= self.down <= 4:
            raise ValueError('down must be 1..4')
        if not 0 <= self.yard_line <= 100:
            raise ValueError('yard_line must be 0..100')
        if self.yards_to_go < 1:
            raise ValueError('yards_to_go must be positive')
        if min(self.timeouts, self.blitzes, self.audibles, self.possessions_left) < 0:
            raise ValueError('resources and possessions cannot be negative')


@dataclass(frozen=True)
class Outcome:
    probability: float
    yards: int = 0
    turnover: bool = False
    points: int = 0


def validate_outcomes(outcomes: Sequence[Outcome]) -> None:
    if not outcomes:
        raise ValueError('at least one outcome is required')
    if any(not 0 <= o.probability <= 1 for o in outcomes):
        raise ValueError('probabilities must be in [0, 1]')
    if abs(sum(o.probability for o in outcomes) - 1.0) > 1e-9:
        raise ValueError('outcome probabilities must sum to 1')


def expected_points(state: GameState) -> float:
    """ILLUSTRATIVE baseline EP, not a learned/calibrated EPA model.

    Assumes offense retains possession; roughly -2..+6 points.
    """
    field_value = -2.0 + 0.08 * state.yard_line
    down_penalty = 0.42 * (state.down - 1)
    distance_penalty = 0.045 * max(0, state.yards_to_go - 10)
    return max(-2.5, min(6.5, field_value - down_penalty - distance_penalty))


def transition(state: GameState, outcome: Outcome) -> tuple[GameState | None, float]:
    """Apply one play. None means this offense's drive ended.

    Terminal drive value is handled by immediate points only; opponent's
    next-drive value is not modeled in this initial version.
    """
    new_yard = state.yard_line + outcome.yards
    if outcome.points:
        return None, float(outcome.points)
    if outcome.turnover or new_yard <= 0:
        return None, 0.0
    if new_yard >= 100:
        return None, 7.0  # placeholder touchdown + extra point
    if outcome.yards >= state.yards_to_go:
        return replace(state, down=1, yard_line=new_yard,
                       yards_to_go=min(10, 100 - new_yard)), 0.0
    if state.down == 4:
        return None, 0.0
    return replace(state, down=state.down + 1, yard_line=new_yard,
                   yards_to_go=state.yards_to_go - outcome.yards), 0.0


def outcome_value(state: GameState, outcome: Outcome,
                  evaluator: Callable[[GameState], float] = expected_points) -> float:
    """Value of a single outcome; use at expectiminimax chance-node leaves."""
    next_state, immediate_points = transition(state, outcome)
    return immediate_points + (evaluator(next_state) if next_state else 0.0)


def expected_action_value(state: GameState, outcomes: Sequence[Outcome],
                          evaluator: Callable[[GameState], float] = expected_points) -> float:
    """Expected points after an action (one probability weighting)."""
    validate_outcomes(outcomes)
    return sum(o.probability * outcome_value(state, o, evaluator) for o in outcomes)


def calculate_epa(state: GameState, outcomes: Sequence[Outcome],
                  evaluator: Callable[[GameState], float] = expected_points) -> float:
    """Expected points added relative to current state's baseline."""
    return expected_action_value(state, outcomes, evaluator) - evaluator(state)


def field_goal_value(make_probability: float) -> float:
    """Expected immediate points; excludes missed-kick field position."""
    if not 0 <= make_probability <= 1:
        raise ValueError('make_probability must be in [0,1]')
    return 3.0 * make_probability


def punt_value(opponent_yard_line: int) -> float:
    """Illustrative possession-swing value; not an EPA calculation."""
    if not 0 <= opponent_yard_line <= 100:
        raise ValueError('opponent_yard_line must be in [0,100]')
    opponent_state = GameState(0, 0, 1, opponent_yard_line, 10)
    return -expected_points(opponent_state)


def audible_improvement(state: GameState,
                        regular_outcomes: Sequence[Outcome],
                        audible_outcomes: Sequence[Outcome]) -> float:
    """Gross expected improvement before accounting for resource use."""
    if state.audibles < 1:
        raise ValueError('no audibles remaining')
    return expected_action_value(state, audible_outcomes) - expected_action_value(state, regular_outcomes)


def evaluate_game_state(state: GameState) -> float:
    """Simple game-aware heuristic; coefficients are tuning placeholders.

    Keep this separate from expected_points: this is a strategic utility,
    not literal expected football points or EPA.
    """
    margin = state.score_for - state.score_against
    urgency = 1.0 / max(1, state.possessions_left)
    return (expected_points(state) + 0.25 * margin * urgency
            + 0.05 * state.timeouts + 0.04 * state.audibles)


def evaluate_actions(state: GameState,
                     dice_actions: Mapping[str, Sequence[Outcome]],
                     field_goal_probability: float | None = None,
                     punt_to_opponent_yard_line: int | None = None) -> dict[str, float]:
    """Compare expected *absolute* action values, not EPA mixed with EP."""
    values = {name: expected_action_value(state, outcomes)
              for name, outcomes in dice_actions.items()}
    if field_goal_probability is not None:
        values['field_goal'] = field_goal_value(field_goal_probability)
    if punt_to_opponent_yard_line is not None:
        if state.down != 4:
            raise ValueError('punting is limited to 4th down in this model')
        values['punt'] = punt_value(punt_to_opponent_yard_line)
    return values


if __name__ == '__main__':
    state = GameState(score_for=7, score_against=10, down=3,
                      yard_line=65, yards_to_go=5, possessions_left=2)
    # Demo only: replace these with the actual results grid probabilities.
    two_dice = [Outcome(.50, yards=2), Outcome(.30, yards=8),
                Outcome(.20, turnover=True)]
    three_dice = [Outcome(.30, yards=0), Outcome(.45, yards=12),
                  Outcome(.25, turnover=True)]
    print('Baseline EP:', round(expected_points(state), 3))
    print('2-dice EPA:', round(calculate_epa(state, two_dice), 3))
    print('3-dice EPA:', round(calculate_epa(state, three_dice), 3))
    print('Action values:', evaluate_actions(state, {
        'roll_2': two_dice, 'roll_3': three_dice}, field_goal_probability=.65))

# Actual probability distributions from Bradley's ResultsGrid CSVs.
# These functions keep the original API intact for agent integration.
from collections import Counter
from itertools import product
from pathlib import Path
import csv

GRID_DIR = Path(__file__).resolve().parent / 'grids'
X_VALUES = {'X1': 13, 'X2': -5, 'X3': 0}  # Bradley's default_x


def _load_grid(filename: str) -> tuple[list[int], list[list[int]]]:
    with (GRID_DIR / filename).open(newline='') as f:
        rows = list(csv.reader(f))
    headers = [int(x) for x in rows[0]]
    values = [[int(X_VALUES.get(cell, cell)) for cell in row] for row in rows[1:]]
    if len(values) != 6 or any(len(row) != len(headers) for row in values):
        raise ValueError(f'{filename}: expected six dice rows matching header columns')
    return headers, values


def dice_outcomes(dice_count: int) -> list[Outcome]:
    """Exact play-outcome probabilities matching ResultsGrid.getPlayResult.

    1 die: row=d1, col=1; 2 dice: row=d1, col=d2;
    3 dice: row=d1, col=d2+d3. Every individual die is fair.
    Encoded 100=touchdown, -100=turnover, others=yards gained/lost.
    """
    if dice_count not in (1, 2, 3):
        raise ValueError('dice_count must be 1, 2, or 3')
    columns, grid = _load_grid('plays.csv')
    lookup = {col: i for i, col in enumerate(columns)}
    counts = Counter()
    for dice in product(range(1, 7), repeat=dice_count):
        col = 1 if dice_count == 1 else dice[1] if dice_count == 2 else dice[1] + dice[2]
        result = grid[dice[0] - 1][lookup[col]]
        counts[result] += 1
    total = 6 ** dice_count
    return [Outcome(count / total, turnover=(result == -100),
                    points=(7 if result == 100 else 0),
                    yards=(0 if abs(result) == 100 else result))
            for result, count in sorted(counts.items())]


def field_goal_probability(distance: int) -> float:
    """Exact probability using Bradley's distance-column selection and one d6."""
    columns, grid = _load_grid('field_goals.csv')
    if len(columns) != 3:
        raise ValueError('field_goals.csv must have three distance columns')
    col = next((i for i, cutoff in enumerate(columns) if distance <= cutoff), 2)
    return sum(bool(row[col]) for row in grid) / 6


def punt_distances() -> list[tuple[int, float]]:
    """Read punt-distance distribution; does not assume unimplemented punt rules."""
    columns, grid = _load_grid('punt.csv')
    counts = Counter(value for row in grid for value in row)
    total = sum(counts.values())
    return [(yards, count / total) for yards, count in sorted(counts.items())]


def evaluate_grid_actions(state: GameState, field_goal_distance: int | None = None) -> dict[str, float]:
    """Score dice actions using the real grid; EP baseline remains illustrative."""
    actions = {'roll_2': dice_outcomes(2), 'roll_3': dice_outcomes(3)}
    if state.yard_line >= 95:
        actions['roll_1'] = dice_outcomes(1)
    probability = (field_goal_probability(field_goal_distance)
                   if field_goal_distance is not None else None)
    return evaluate_actions(state, actions, field_goal_probability=probability)

def evaluate_bradley_state(bradley_state):
    offense = bradley_state.offense
    defense = 1 - offense

    state = GameState(
        score_for=bradley_state.scores[offense],
        score_against=bradley_state.scores[defense],
        down=bradley_state.down,
        yard_line=100 - bradley_state.yttd,
        yards_to_go=bradley_state.ytfd,
        timeouts=bradley_state.time_outs[offense],
        blitzes=bradley_state.blitzes[defense],
        audibles=bradley_state.audibles[offense],
        possessions_left=(bradley_state.drives_remaining + 1) // 2
    )

    return expected_points(state)
