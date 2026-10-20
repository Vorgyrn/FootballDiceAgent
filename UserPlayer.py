
class Player:
    score=0
    def __init__(self, name="Human", role=None):
        self.name = name
        # 0 for p1, 1 for p2
        self.role = role

    def determine_plays(self, state):
        # determine offensive actions for the given game state
        actions = []
        if self.role == state.offense:
            actions = self.determine_off_plays(state)
        else: 
            actions = self.determine_def_plays(state)
            
        return actions

    def determine_off_plays(self, state):
        # determine offensive actions for the given game state
        actions = ["2d", "3d", "pt"]
        if state.audibles[self.role] > 0:
            actions.append("ad")
        elif state.yttd <= 5:
            actions.append("1d")
        elif state.yttd < 47:
            actions.append("fg")

        return actions

    def determine_def_plays(self, state):
        # determine defensive actions for the given game state
        actions = []
        if state.audibles[self.role] > 0:
            actions.append("ad")
        elif state.blitzes[self.role] > 0:
            actions.append("bz")
            
        return actions
    
    def __repr__(self):
        return f"{self.name}"


class UserPlayer(Player):
    def __init__(self, name="Human", role=0):
        super().__init__(name=name, role=role)


class AgentPlayer(Player):
    def __init__(self, name="Agent", role=1):
        super().__init__(name=name, role=role)
