
class UserPlayer:
    score=0
    def __init__(self, name="Human", role=None):
        self.name = name
        # 1 for p1, 2 for p2
        self.role = role
        
    def __repr__(self):
        return f"{self.name}"
