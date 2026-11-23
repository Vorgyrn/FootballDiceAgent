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
    def call_blitz(self, state):
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
        if yards == -100: yards = "turnover"
        print_red(f'{self.name} last play resulted in {yards}')
        print(f"Take a timout to redo play?")
        i = 1
        for play in ops:
            print(f'\t{i}. {play}')
            i += 1

        return ops[validate_input(len(ops))]
    
    def call_audible(self, state):
        # determine actions for the given game state
        raise NotImplementedError
    
    def call_blitz(self, state):
        # determine actions for the given game state
        raise NotImplementedError

class AgentPlayer(Player):
    def __init__(self, name="Agent", role=1):
        super().__init__(name=name, role=role)

    def call_play(self, state):
        raise NotImplementedError
