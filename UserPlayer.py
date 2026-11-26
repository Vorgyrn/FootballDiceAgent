from utils import *

import sys
class Player:
    score=0
    def __init__(self, name="Human", role=None):
        self.name = name
        # 0 for p1, 1 for p2
        self.role = role

    def call_play(self, state):
        # determine actions for the given game state
        raise NotImplementedError

    def call_time_out(self, state):
        # determine actions for the given game state
        raise NotImplementedError
    def call_audible(self, state):
        # determine actions for the given game state
        raise NotImplementedError
    def call_blitz(self, state, table):
        # determine actions for the given game state
        raise NotImplementedError
    def __repr__(self):
        return f"{self.name}"


class UserPlayer(Player):
    def __init__(self, name="Human", role=0):
        super().__init__(name=name, role=role)

    def call_play(self, state):
        ops = len(state.offense_plays) if state.offense == self.role else len(state.defense_plays)
        return validate_input(ops)

    def call_time_out(self, state, yards=0):
        # determine actions for the given game state
        ops = ["yes", "no"]
        print(f"Take a timout to redo play?")
        i = 1
        for play in ops:
            print(f'\t{i}. {play}')
            i += 1

        return ops[validate_input(len(ops))]
    
    def call_audible(self, state):
        # determine actions for the given game state
        ops = range(1,7)
        print(f"Select a row for the play to come from:")
        i = 1
        for play in ops:
            print(f'\t{i}. {play}')
            i += 1
        # +1 becuase validate does -1 to normalize for 0 
        #   base but this index is 1 based
        return validate_input(len(ops))+1
    
    def call_blitz(self, state, table):
        # determine actions for the given game state
        print("Select row of cell to remove for the play:")
        row = validate_input(len(table.index))+1
        print("Select column of cell to remove for the play:")
        col = validate_input(len(table.columns))+1
        return [row, col]

class AgentPlayer(Player):
    def __init__(self, name="Agent", role=1):
        super().__init__(name=name, role=role)

    def call_play(self, state):
        raise NotImplementedError
