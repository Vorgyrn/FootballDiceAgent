from collections import defaultdict
from collections.abc import Callable
from typing import Any


DICE_SUMS = [[first + second for second in range(1, 7)]
             for first in range(1, 7)]
DICE_PROBABILITIES = [[1.0 / 36.0 for _ in range(6)]
                      for _ in range(6)]


def preprocess_rolls(
    state: Any,
    action: Any,
    resolve: Callable[[Any, Any, int, int], tuple[Any, float]],
    expected_points: Callable[[Any], float],
) -> list[list[dict[str, Any]]]:
    """Return grid[first_die-1][second_die-1] of chance outcomes.
    """
    before = expected_points(state)
    grid = []
    for d1 in range(1, 7):
        row = []
        for d2 in range(1, 7):
            next_state, immediate_points = resolve(state, action, d1, d2)
            p = DICE_PROBABILITIES[d1 - 1][d2 - 1]
            epa = immediate_points + expected_points(next_state) - before
            row.append({
                "dice": (d1, d2),
                "sum": d1 + d2,
                "probability": p,
                "next_state": next_state,
                "epa": epa,
                "weighted_epa": p * epa,
            })
        grid.append(row)
    return grid


def expected_epa(grid: list[list[dict[str, Any]]]) -> float:
    """Value of the chance node for this action, before later decisions."""
    return sum(cell["weighted_epa"] for row in grid for cell in row)


def group_by_sum(grid: list[list[dict[str, Any]]]) -> dict[int, dict[str, float]]:
    """Optional 11-row view; keeps probabilities and EPA correctly weighted."""
    result = defaultdict(lambda: {"probability": 0.0, "weighted_epa": 0.0})
    for row in grid:
        for cell in row:
            group = result[cell["sum"]]
            group["probability"] += cell["probability"]
            group["weighted_epa"] += cell["weighted_epa"]
    return dict(sorted(result.items()))


if __name__ == "__main__":
    # Synthetic fixture: state is only a number, NOT a football game state.
    # Replace this resolver with a lookup in your real action-specific stat chart.
    def demo_resolve(state: int, action: str, d1: int, d2: int) -> tuple[int, float]:
        synthetic_gain = d1 + d2 - 6
        return state + synthetic_gain, 0.0

    def demo_ep(state: int) -> float:
        return state / 10.0  # Synthetic EP, NOT fitted football data.

    grid = preprocess_rolls(50, "run", demo_resolve, demo_ep)
    print("Dice sums (rows = die 1, columns = die 2):")
    for row in DICE_SUMS:
        print(*row)
    print("Expected EPA:", round(expected_epa(grid), 3))
    print("Example cell (1, 1):", grid[0][0])
    print("P(sum=7):", group_by_sum(grid)[7]["probability"])
