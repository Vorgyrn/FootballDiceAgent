{\rtf1\ansi\ansicpg1252\cocoartf2870
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww34000\viewh18420\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from itertools import product\
\
# Football Dice project\
# Architecture: Game state input - grid of dice probabilities\
# Calculates possible outcomes for rolling 1, 2, or 3 dice.\
\
def dice_probabilities(num_dice):\
    outcomes = list(product(range(1, 7), repeat=num_dice))\
\
    # Each combination has the same probability\
    probability = 1 / len(outcomes)\
\
    results = \{\}\
    for outcome in outcomes:\
        results[outcome] = probability\
\
    return results\
\
\
# Test the function with different numbers of dice\
for dice in [1, 2, 3]:\
    results = dice_probabilities(dice)\
\
    print("Dice:", dice)\
    print("Possible outcomes:", len(results))\
    print("Total probability:", sum(results.values()))\
    print()\
\
\
# Check that the number of outcomes is correct\
assert len(dice_probabilities(1)) == 6\
assert len(dice_probabilities(2)) == 36\
assert len(dice_probabilities(3)) == 216\
\
print("All tests passed!")}