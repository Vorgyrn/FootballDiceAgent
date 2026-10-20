import random

def roll_n_d6(n=1):
    if n < 1: raise ValueError(f"n must be > 0, got {n}")
    return [random.randint(1, 6) for _ in range(n)]


def roll_1_d6():
    return roll_n_d6(1)[0]
