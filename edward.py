
from itertools import product

# ============================================================
# FOOTBALL DICE AI - DICE PROBABILITY CALCULATOR
# ============================================================
#
# ARCHITECTURE REFERENCE:
#
# Section: "Game state input to agent" 
#   - Grid of dice probabilities
#   - Preprocessed results mapped to probabilities
#
# Section: "Actions" 
#   - Offense can roll 2 dice or 3 dice
#   - Offense can roll 1 die within the defense's 5-yard lane
#
# Section: "Agent decision making"
#   - Calculate EPA for each action
#   - Explore possible dice-roll outcomes
#
# PURPOSE:
# Calculate the probability of each possible dice combination.
# These probabilities will eventually be used by the
# Expectiminimax agent to evaluate offensive actions.
#
# NOTE:
# This function does not calculate EPA or implement the
# game's statistics chart. Those require additional rules.
# ============================================================


def dice_probabilities(num_dice):
    """
    Generate all possible outcomes for rolling num_dice
    standard six-sided dice.

    Returns:
        Dictionary mapping dice combinations to probabilities.
    """

    # ARCH: Actions - Roll 1, 2, or 3 dice
    # Generate every possible ordered combination.
    outcomes = list(
        product(range(1, 7), repeat=num_dice)
    )

    # ARCH: Game state input - Grid of dice probabilities
    # Assume each die is fair and rolls independently.
    probability = 1 / len(outcomes)

    # Assign the probability to each outcome.
    return {
        outcome: probability
        for outcome in outcomes
    }


# ============================================================
# TESTING
# ============================================================

# ARCH: Actions - Roll 2 dice
two_dice = dice_probabilities(2)

print("Two dice possible outcomes:", len(two_dice))
print("Probability of (1, 1):", two_dice[(1, 1)])


# ARCH: Actions - Roll 3 dice
three_dice = dice_probabilities(3)

print("Three dice possible outcomes:", len(three_dice))
print("Probability of (1, 1, 1):", three_dice[(1, 1, 1)])


# ARCH: Actions - Roll 1 die within 5-yard lane
one_die = dice_probabilities(1)

print("One die possible outcomes:", len(one_die))


# Verify probabilities sum to 1.
assert abs(sum(one_die.values()) - 1.0) < 1e-9
assert abs(sum(two_dice.values()) - 1.0) < 1e-9
assert abs(sum(three_dice.values()) - 1.0) < 1e-9

print("All probability tests passed!")
