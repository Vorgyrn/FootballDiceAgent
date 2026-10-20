
class Player:
    score=0
    def __init__(self, name="Human", role=None):
        self.name = name
        # 0 for p1, 1 for p2
        self.role = role

    def call_play(self, state):
        # determine offensive actions for the given game state
        actions = []
        if self.role == state.offense:
            actions = self.call_off_play(state)
        else: 
            actions = self.call_def_play(state)
            
        return actions


    def call_off_play(self, state):
        raise NotImplementedError
    
    def call_def_play(self, state):
        raise NotImplementedError
    
    
    def __repr__(self):
        return f"{self.name}"


class UserPlayer(Player):
    def __init__(self, name="Human", role=0):
        super().__init__(name=name, role=role)

    def call_off_play(self, state):
        raise NotImplementedError
    
    def call_def_play(self, state):
        raise NotImplementedError

class AgentPlayer(Player):
    def __init__(self, name="Agent", role=1):
        super().__init__(name=name, role=role)

    def call_off_play(self, state):
        raise NotImplementedError
    
    def call_def_play(self, state):
        raise NotImplementedError
