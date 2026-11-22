from utils import *
from UserPlayer import UserPlayer
from ResultsGrid import ResultsGrid

class GameState:
    # game data 
    OFFENSE = 0
    DEFENSE = 1
    
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

        self.offense_plays = []
        self.defense_plays = []

        
    def change_possession(self, new_pos:int):
        # change game state to swap offense and defense roles
        # input: new_pos    new ball spot [1,99]
        self.drives_remaining -= 1
        if self.offense == 1: self.offense = 0
        else: self.offense = 1

        self.down = 1
        self.yttd = new_pos
        if new_pos < 10: self.ytfd = new_pos
        else: self.ytfd = 10
    
    def display_state(self):
        # TODO: impliment a way to display all game state info to user nicely
        # (includeing printing the field to screen)
        print(f'P1 {self.scores[0]} : P2 {self.scores[1]}')
        print(f'Player {self.offense+1} on offense, {self.drives_remaining} drives left')

    def isWinning(self, player):
        # check if a player is winning or not, 0 check player 1, 1 check player2
        return player == self.scores.index(max(self.scores))
        
class FootballDice:
    # game manager
    PRE_PLAY_ACTIONS_OFF = ['Audible']
    PLAYS_OFF = ["Roll 1 dice (special scoring action)", 'Roll 2 dice', 'Roll 3 dice', "Attempt field goal (special scoring action)", 'Short Punt (1 dice)', 'Long Punt (2 dice)']
    ALL_OFF_ACTIONS = PLAYS_OFF + PRE_PLAY_ACTIONS_OFF
    ALL_DEF_ACTIONS = ['None', 'Audible', 'Blitz']
    
    def __init__(self, player1, player2, possessions=3):
        self.p1 = player1
        self.p2 = player2

        self.playResults = ResultsGrid()
        
        self.setup_game(possessions)
        print('\n')
        self.play_game()

    def setup_game(self, possessions):
        # Initialize the game state and determine who plays first
        print("Starting a game of Football dice!")

        # must reroll until winner
        tie = True
        while(tie):
            print(f"Rolling to determine first possession...")
            p1Roll, p2Roll = roll_2_d6()
            print(f"{self.p1} rolled a {p1Roll}!")
            print(f"{self.p2} rolled a {p2Roll}!")
            
            tie = p1Roll == p2Roll
            
            if tie:
                print("Players tied! Must reroll")
            elif p1Roll > p2Roll:
                print(f"{self.p1} will start on offense!")
                self.state = GameState(0, possessions)
                self.offense = self.p1
                self.defense = self.p2
            else:
                print(f"{self.p2} will start on offense!")
                self.state = GameState(1, possessions)
                self.offense = self.p2
                self.defense = self.p1

        self.state.display_state()


    def determine_off_plays(self):
        # determine offensive actions for the given game state
        actions = ["Roll 2 dice", "Roll 3 dice"]
        if self.state.yttd <= 5:
            actions.append("Roll 1 dice (special scoring action)")
        if self.state.yttd < 47:
            actions.append("Attempt field goal (special scoring action)")
        if self.state.audibles[self.offense.role] > 0:
            actions.append("Audible")
        if self.state.down == 4:
            actions.append('Short Punt (1 dice)')
            actions.append('Long Punt (2 dice)')

        return actions

    def determine_def_plays(self):
        # determine defensive actions for the given game state
        actions = ['None']
        if self.state.audibles[self.defense.role] > 0:
            actions.append("Audible")
        if self.state.blitzes[self.defense.role] > 0:
            actions.append("Blitz")
            
        return actions
    
    def play_game(self):
        while (self.state.drives_remaining > 0) or \
                (self.state.scores[0] == self.state.scores[1]):
            
            # determine offense possible actions
            self.state.offense_plays = self.determine_off_plays()
            # determine defense possible actions
            self.state.defense_plays = self.determine_def_plays()
            
            # get offensve action 
            off_play = self.off_call_play()
            # get defensive action (will they blitz?)
            # def_play = self.def_call_play()

            # TODO: CHANGE GRID STATES BASED ON DEFENSIVE ACTION pre dice roll

            # resolve offense special actions
            if off_play in self.PRE_PLAY_ACTIONS_OFF: 
                self.resolve_pre_play_actions(off_play)
            self.play_down(off_play)

            print('')
            print(f'Score:')
            print(f'{self.p1}: {self.state.scores[0]}')
            print(f'{self.p2}: {self.state.scores[1]}')
            #print_blue(f'{self.offense} on offense')
            print('')

        print(f'Final Score:')
        print(f'{self.p1}: {self.state.scores[0]}')
        print(f'{self.p2}: {self.state.scores[1]}')
        winner = self.state.scores.index(max(self.state.scores))
        print_green(f'\nWINNER: {self.p1 if winner else self.p2}: {self.state.scores[winner]}')
        
        
    def off_call_play(self):
        # prompt offense for play call
        print(f"Select Offensive play for {self.offense.name}")
        i = 1
        for play in self.state.offense_plays:
            print(f'\t{i}. {play}')
            i += 1
        val = self.offense.call_play(self.state)
        return self.state.offense_plays[val]

    def def_call_play(self):
        # prompt defense for play call
        print(f"Select Defensive play for {self.defense.name}")
        i = 1
        for play in self.state.defense_plays:
            print(f'\t{i}. {play}')
            i += 1
        val = self.defense.call_play(self.state)
        return  self.state.defense_plays[val]

    # core game functions
    def change_possesion(self, new_pos:int):
        # change game state to swap offense and defense roles
        # input: new_pos    new ball spot [1,99]
        self.state.change_possession(new_pos)
        if self.state.offense == 1: 
            self.offense = self.p2
            self.defense = self.p1
        else: 
            self.offense = self.p1
            self.defense = self.p2
        print(f"{self.offense} is now on offense at the {self.state.yttd}!")
        print(f"1st and {self.state.ytfd}!")
            
    def resolve_pre_play_actions(self, play):
        pass
    
    def play_down(self, play):
        res = None
        print_yellow(f'{self.offense} is running {play}')
        roll = roll_3_d6()
        
        if play == "Roll 1 dice (special scoring action)":
            roll = roll[:1]
            print(f'Offense rolled {roll}')
            res = self.playResults.getPlayResult(roll)
            
        elif play =='Roll 2 dice':
            roll = roll[:2]
            print(f'Offense rolled {roll}')
            res = self.playResults.getPlayResult(roll)
            
        elif play == 'Roll 3 dice':
            print(f'Offense rolled {roll}')
            res = self.playResults.getPlayResult(roll)
            
        elif play == "Attempt field goal (special scoring action)":
            roll = roll[:1]
            print(f'Offense rolled {roll}!')
            res = self.playResults.getFieldGoalResult(roll, self.state.yttd)
        elif "Punt" in play:
            if "Short" in play: roll = roll[:1]
            else: roll = roll[:2]
            
            print(f'Offense rolled {roll}!')
            res = self.playResults.getPuntResult(roll)
            
        self.evaluate_play(play, res)

    def evaluate_play(self, play:str, res:int):
        if "Roll" in play:
            if res == -100:
                # the play resulted in a turn over
                print_red(f'{self.offense} turned over the ball!')
                self.change_possesion(100-self.state.yttd)
            elif res == 100 or (res == self.state.yttd):
                # the play resulted in a touchdown
                print_green(f'{self.offense} scored a touchdown!')
                self.state.scores[self.state.offense] += 7
                self.doKickoff()
            else: 
                # play went too far == no gain, also no safeties in football dice
                if res > self.state.yttd or ((self.state.yttd - res) > 99): 
                    print_red('NO GAIN!')
                    res = 0
                else: print_green(f'{res} yard gain')
                                
                # check for turn over on downs
                if self.state.down == 4 and ((self.state.ytfd-res) > 0): 
                    print_red(f'{self.offense} turned over the ball on downs!')
                    self.change_possesion(100-(self.state.yttd+res))
                elif (self.state.ytfd-res) <= 0:
                    # the team got a first down
                    self.state.down = 1
                    self.state.yttd -= res
                    self.state.ytfd = 10
                    if self.state.yttd < 10:
                        # first down should be first and goal
                        self.state.ytfd = self.state.yttd
                else: 
                    # did not result in first down or change of possession, advance down and position
                    self.state.down += 1
                    self.state.yttd -= res
                    self.state.ytfd -= res
                
                print('')
                if self.state.down == 4: print_red(f'DOWN: {self.state.down}')
                else: print_blue(f'DOWN: {self.state.down}')
                print_blue(f'Yards to First Down: {self.state.ytfd}')
                print_blue(f'Yards to End Zone: {self.state.yttd}')
                
        elif "Punt" in play:
            # calculate new position of ball after punt
            new_pos = self.state.yttd - res
            if res == 0: print('Blocked punt!')
            elif new_pos <= 1:
                # punt went into endzone
                print_red(f'The punt went for {res} and into the endzone, touch back!')
                new_pos=25 
                self.change_possesion(new_pos)
            else: 
                print(f'{self.offense} punted the ball {res} yards')
                self.doKickReturn(100 - new_pos)
                
        elif "goal" in play:
            if res: 
                # fg good, add 3 points and do kickoff
                print_green("Field Goal attempt is good!")
                self.state.scores[self.state.offense] += 3
                # TODO: create function to do a kickoff
                self.doKickoff()
            else: 
                # fg no good, def gets ball at current position
                print_red("Field Goal attempt is no good!")
                self.change_possesion(100-self.state.yttd)            
            
    def doKickoff(self):
        print_green("Kicking from the 50")
        plays = ['Short Kick (1 dice)', 'Long Kick (2 dice)']
        if self.state.isWinning(self.defense.role):
            plays.append('Onside Kick')
        self.state.offense_plays = plays
        play = self.off_call_play()

        if "Onside" in play:
            if self.onsideKick():
                print_green(f'{self.offense} onside kick was a success!')
                self.state.yttd = 50
                self.state.ytfd = 10
                self.state.down = 1
            else: self.change_possesion(50)
                   
        else:
            roll = [12]
            start = 50
            # roll dice until non 12 is hit
            while(sum(roll) == 12):
                roll = roll_2_d6()
                print_yellow(f"{self.offense} rolled {roll}")
                if sum(roll) == 12: print_red(f"Bad kick, {self.offense} must reroll!")
            dist = self.playResults.getPuntResult(roll)
            if dist >= start:
                print_red("Touch back, the ball will be place at the 25")
                start = 75
                self.change_possesion(start)
            else: 
                start = 100-(start-dist)
                print_green(f"Kick goes to the {start}")
                self.doKickReturn(start)
            
    def doKickReturn(self, start):
        # prompt user if they want to try to return the ball
        print(f"Ball on the {start}")
        plays = ['Return (Roll 3 dice)', "Don't return"]
        self.state.offense_plays = plays
        play = self.off_call_play()
        
        if "Roll" in play:
            roll = roll_3_d6()
            res = self.playResults.getPlayResult(roll)
            if res == -100:
                # the play resulted in a turn over
                print_red(f'{self.defense} turned over the ball!')
                self.change_possesion(100-start)
            elif res == 100:
                # the play resulted in a touchdown
                print_green(f'{self.defense} scored a touchdown!')
                self.state.scores[self.defense.role] += 7
                self.doKickoff()
            else: 
                # no safeties in fbdice
                if ((start - res) > 99): 
                    print_red('NO GAIN!')
                    res = 0
                else: print_green(f'{res} yard gain')

                self.change_possesion(start-res)
            
        elif "Don't" in play:
            print(f"{self.defense} is calling a fair catch")
            self.state.change_possession(start)
            

    def onsideKick(self):
        # roll 3 dice and must get the following results
        # d1 = 1,2,3
        # d2 and d3 = 5,6
        # returns TRUE for success, FALSE for fail
        roll = roll_3_d6()
        print_yellow(f"{self.offense} rolled {roll}")
        return (roll[0] < 4) and  (roll[1] > 4) and  (roll[2] > 4)
        
if __name__ == "__main__":
     p1 = UserPlayer("Brad", 0)
     p2 = UserPlayer("Sav", 1)
     game = FootballDice(p1, p2, possessions=6)
