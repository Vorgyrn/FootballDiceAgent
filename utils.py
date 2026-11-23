import random
import sys

def roll_n_d6(n=1):
    if n < 1: raise ValueError(f"n must be > 0, got {n}")
    return [random.randint(1, 6) for _ in range(n)]

def roll_3_d6():
    return roll_n_d6(3)

def roll_2_d6():
    return roll_n_d6(2)

def roll_1_d6():
    return roll_n_d6(1)



def print_red(text):
    print(f"\033[31m{text}\033[0m")

def print_green(text):
    print(f"\033[32m{text}\033[0m")

def print_blue(text):
    print(f"\033[34m{text}\033[0m")

def print_yellow(text):
    print(f"\033[33m{text}\033[0m")

def validate_input(num_ops):
    # takes the number of acceptable chioces is 1-n
    # returns the input value -1 to be index of list
    valid = False
    while(not valid):
        try:
            val = int(input("Choice: ").strip().split()[0])
            if val > num_ops or val < 1:
                print(f"Invalid input {val}, try again")
            else: valid = True
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            print("Invalid input, try again")
    print('')
    return val-1
