from utils import roll_1_d6
from UserPlayer import UserPlayer

class GameState:
    def __init__(self, offense=0, possesions=3):
        # In each list the first element is related to player 1 while 
        #   the second is for player 2
        
        self.scores = [0, 0] 
        # 1 possession == one drive for each player
        #   - 1 because the offense is starting with a drive
        self.drives_remaining = (possesions * 2) - 1
        
        # expendables 
        self.time_outs = [3, 3]
        self.audibles = [5, 5]
        self.blitzes = [5, 5]
    
        # drive details
        # 0 for p1, 1 for p2
        self.offense = offense
        self.down = 1
        
        # yards to first down
        self.ytfd = 10
        
        # More simple to represent field as [1,99], 
        #   will do 99-yttd if possession flips
        # yards to touchdown
        self.yttd = 75 

        # TODO: add probability board here
        
    def display_state(self):
        # TODO: impliment a way to display all game state info to user nicely
        # (includeing printing the field to screen)
        print(f'P1 {self.scores[0]} : P2 {self.scores[1]}')
        print(f'Player {self.offense+1} on offense, {self.drives_remaining} drives left')
        

class FootballDice:
    def __init__(self, player1, player2, possessions=3):
        self.p1 = player1
        self.p2 = player2
        
        self.setup_game(possessions)

    def setup_game(self, possessions):
        # Initialize the game state and determine who plays first
        print("Starting a game of Football dice!")

        # must reroll until winner
        tie = True
        while(tie):
            print(f"Rolling to determine first possession...")
            p1Roll = roll_1_d6()
            p2Roll = roll_1_d6()
            print(f"{self.p1} rolled a {p1Roll}!")
            print(f"{self.p2} rolled a {p2Roll}!")
            
            tie = p1Roll == p2Roll
            
            if tie:
                print("Players tied! Must reroll")
            elif p1Roll > p2Roll:
                print(f"{self.p1} will start on offense!")
                self.state = GameState(0, possessions)
            else:
                print(f"{self.p2} will start on offense!")
                self.state = GameState(1, possessions)

        self.state.display_state()

            

if __name__ == "__main__":
     p1 = UserPlayer("Brad", 0)
     print(p1)
     p2 = UserPlayer("Sav", 1)
     print(p2)
     
     game = FootballDice(p1, p2)
