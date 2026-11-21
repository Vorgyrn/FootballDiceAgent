from itertools import product

# Football Dice project
# Architecture: Game state input - grid of dice probabilities
# Calculates possible outcomes for rolling 1, 2, or 3 dice.

def dice_probabilities(num_dice):
    outcomes = list(product(range(1, 7), repeat=num_dice))

    # Each combination has the same probability
    probability = 1 / len(outcomes)

    results = {}
    for outcome in outcomes:
        results[outcome] = probability

    return results


# Test the function with different numbers of dice
for dice in [1, 2, 3]:
    results = dice_probabilities(dice)

    print("Dice:", dice)
    print("Possible outcomes:", len(results))
    print("Total probability:", sum(results.values()))
    print()


# Check that the number of outcomes is correct
assert len(dice_probabilities(1)) == 6
assert len(dice_probabilities(2)) == 36
assert len(dice_probabilities(3)) == 216

print("All tests passed!")


# Calculate expected value using dice probabilities
def calculate_expected_value(num_dice, outcome_values):
    probabilities = dice_probabilities(num_dice)

    expected_value = 0

    for outcome, probability in probabilities.items():
        value = outcome_values[outcome]
        expected_value += probability * value

    return expected_value


# Simple test using one die
# These are example values, not actual football EPA values
example_values = {
    (1,): -2,
    (2,): -1,
    (3,): 0,
    (4,): 1,
    (5,): 2,
    (6,): 3
}

result = calculate_expected_value(1, example_values)

print("Expected value:", round(result, 2))

assert abs(result - 0.5) < 0.000001
print("Expected value test passed!")
