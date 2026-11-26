from utils import *
from UserPlayer import UserPlayer
from ResultsGrid import ResultsGrid

import copy

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
        self.off_play_call = ""
        self.def_play_call = ""

        self.aud_row = None
        self.def_blitz = None

        
    def change_possesion(self, new_pos:int):
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
        
        print(f'Score    | {self.scores[0]} | {self.scores[1]} |')
        print(f'TOs      | {self.time_outs[0]} | {self.time_outs[1]} |')
        print(f'Audibles | {self.audibles[0]} | {self.audibles[1]} |')
        print(f'Blitzes  | {self.blitzes[0]} | {self.blitzes[1]} |')
        print(f'Drives Remaining: {self.drives_remaining}')

        if self.down == 1: print_blue(f'DOWN: {self.down}')
        elif self.down == 2: print_green(f'DOWN: {self.down}')
        elif self.down == 3: print_yellow(f'DOWN: {self.down}')
        else: print_red(f'DOWN: {self.down}')
        print_blue(f'Yards to First Down: {self.ytfd}')
        print_blue(f'Yards to End Zone: {self.yttd}')

    def isWinning(self, player):
        # check if a player is winning or not, 0 check player 1, 1 check player2
        return player == self.scores.index(max(self.scores))

    def getOffTimeouts(self):
        return self.time_outs[self.offense]

    def reset_play_calls(self):
        # reset calls from the last play
        self.offense_plays = []
        self.defense_plays = []
        self.off_play_call = ""
        self.def_play_call = ""

        self.aud_row = None
        self.def_blitz = None
        
class FootballDice:
    # game manager
    PRE_PLAY_ACTIONS_OFF = ['Audible']
    OFF_BASE_PLAYS = ["Roll 2 dice", "Roll 3 dice"]
    PLAYS_OFF = OFF_BASE_PLAYS + ["Roll 1 dice (special scoring action)", "Attempt field goal (special scoring action)", 'Short Punt (1 dice)', 'Long Punt (2 dice)']
    ALL_OFF_ACTIONS = PLAYS_OFF + PRE_PLAY_ACTIONS_OFF
    ALL_DEF_ACTIONS = ['None', 'Audible', 'Dice Change Blitz', 'Cross Out Blitz']
    
    def __init__(self, player1, player2, possessions=3):
        self.p1 = player1
        self.p2 = player2
        self.playResults = ResultsGrid()
        self.setup_game(possessions)
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

        self.display_state()

    def display_state(self):
        print('')
        print(f'Player | {self.p1} | {self.p2} |')
        self.state.display_state()
        print(f'Player {self.offense} on offense')
        print('')
        
    def determine_off_plays(self):
        # determine offensive actions for the given game state
        actions = copy.deepcopy(self.OFF_BASE_PLAYS)
        if self.state.yttd <= 5:
            actions.append("Roll 1 dice (special scoring action)")
        if self.state.yttd < 47:
            actions.append("Attempt field goal (special scoring action)")
        if self.state.audibles[self.offense.role] > 0:
            actions.append("Audible")
        if self.state.down == 4:
            actions.append('Short Punt (1 dice)')
            actions.append('Long Punt (2 dice)')

        self.state.offense_plays = actions

    def determine_def_plays(self):
        # determine defensive actions for the given game state
        actions = ['None']
        if self.state.audibles[self.defense.role] > 0 and \
            "Roll" in self.state.off_play_call:
            actions.append("Audible")
        if self.state.blitzes[self.defense.role] > 0:
            # the defense can cross out a number from any result chart (kick,fg,play)
            actions.append("Cross Out Blitz")
            if "Roll" in self.state.off_play_call:
                # can only use this if the offense is using a normal play
                if "2" not in self.state.off_play_call:
                    actions.append("2 Dice Blitz")
                if "3" not in self.state.off_play_call:
                    actions.append("3 Dice Blitz")
            

        self.state.defense_plays = actions
    
    def play_game(self):
        while (self.state.drives_remaining > 0) or \
                (self.state.scores[0] == self.state.scores[1]):
            
            self.state.reset_play_calls()
            # off play call and resolution
            self.determine_off_plays()
            self.off_call_play()
            self.resolve_off_pre_play_actions()
            
            # def play call and resolution
            self.def_call_play()
            self.resolve_def_pre_play_actions()

            # run play and update game state
            self.play_down()         
            self.display_state()

        print(f'Final Score:')
        print(f'{self.p1}: {self.state.scores[0]}')
        print(f'{self.p2}: {self.state.scores[1]}')
        winner = self.state.scores.index(max(self.state.scores))
        print_green(f'\nWINNER: {self.p1 if winner else self.p2}: {self.state.scores[winner]}')
          
    def off_call_play(self):
        # prompt offense for play call and set result in game state        
        print(f"Select Offensive play for {self.offense.name}")
        i = 1
        for play in self.state.offense_plays:
            print(f'\t{i}. {play}')
            i += 1
        val = self.offense.call_play(self.state)
        self.state.off_play_call = self.state.offense_plays[val]
        return self.state.off_play_call

    def def_call_play(self):
        # prompt defense for play call
        self.determine_def_plays()
        
        print(f"Select Defensive play for {self.defense.name}")
        i = 1
        for play in self.state.defense_plays:
            print(f'\t{i}. {play}')
            i += 1
        val = self.defense.call_play(self.state)
        
        self.state.def_play_call = self.state.defense_plays[val]
        return self.state.def_play_call

    # core game functions
           
    def resolve_def_pre_play_actions(self):
        dp = self.state.def_play_call
        # all defensive actions are pre play so anything other than none requires handling
        if dp == "Audible":
            if self.state.aud_row is not None:
                print_red(f"{self.defense} is overriding the audible called by {self.offense}")
                self.state.audibles[self.offense.role] += 1
            # set game state varaible to set def blitz row (replace first dice roll in offense play)
            self.state.aud_row = self.defense.call_audible(self.state)
            self.state.audibles[self.defense.role] -= 1
            print_yellow(f"Defense is forcing play results to row {self.state.aud_row}")
            print("Options:")
            print(self.playResults.getPlayRow(self.state.aud_row).to_list())
            
        elif dp == '2 Dice Blitz':
            print_yellow(f"Defense is forcing the offense to roll 2 dice")
            self.state.off_play_call = "Roll 2 dice"
            self.state.blitzes[self.offense.role] -= 1
            
        elif dp == '3 Dice Blitz':
            print_yellow(f"Defense is forcing the offense to roll 3 dice")
            self.state.off_play_call = "Roll 3 dice"
            self.state.blitzes[self.offense.role] -= 1
            
        elif dp == 'Cross Out Blitz':
            op = self.state.off_play_call
            
            grid = None
            if op == "Roll 1 dice (special scoring action)":
                grid = self.playResults.get1DiceGrid()
                
            elif op =='Roll 2 dice':
                grid = self.playResults.get2DiceGrid()
                
            elif op == 'Roll 3 dice':
                grid = self.playResults.get3DiceGrid()
                
            elif op == "Attempt field goal (special scoring action)":
                grid = self.playResults.getFGGrid()
            
            elif "Short" in op:
                grid = self.playResults.getShortKickGrid()

            elif "Long" in op:
                grid = self.playResults.getLongKickGrid()

            print_yellow("Options to cross out:")
            print(grid.to_string())
        
            self.state.def_blitz = self.defense.call_blitz(self.state, grid)
            self.state.blitzes[self.offense.role] -= 1
            print_red(f'Defense is blocking results from {self.state.def_blitz}')
            

    def resolve_off_pre_play_actions(self):
        # only pre play action for offense is audible
        if self.state.off_play_call in self.PRE_PLAY_ACTIONS_OFF:
            self.state.aud_row = self.offense.call_audible(self.state)
            self.state.audibles[self.offense.role] -= 1
            print_yellow(f"Offense is forcing play results to row {self.state.aud_row}")
            print("Options:")
            print(self.playResults.getPlayRow(self.state.aud_row).to_list())
            
            # call actual play
            print(self.OFF_BASE_PLAYS)
            self.state.offense_plays = self.OFF_BASE_PLAYS
            print(self.state.offense_plays)
            self.off_call_play() 
        
    def play_down(self):
        play = self.state.off_play_call
        res = None
        attempt = True
        print_yellow(f'{self.offense} is running {play}')
        
        while(attempt):
            attempt = False
            roll = roll_3_d6()

            if self.state.aud_row is not None: 
                roll[0] = self.state.aud_row
            
            if play == "Roll 1 dice (special scoring action)":
                if self.state.def_blitz and self.state.def_blitz[0] == roll[0]:
                    print_red("Rolled disabled cell, reroll!")
                    attempt = True
                    continue
                
                roll = roll[:1]
                print(f'Offense rolled {roll}')
                res = self.playResults.getPlayResult(roll)
                print_yellow(f'')
                
            elif play =='Roll 2 dice':
                if self.state.def_blitz and self.state.def_blitz == roll:
                    print_red("Rolled disabled cell, reroll!")
                    attempt = True
                    continue
                roll = roll[:2]
                print(f'Offense rolled {roll}')
                res = self.playResults.getPlayResult(roll)
                
            elif play == 'Roll 3 dice':
                r = [roll[0], roll[1]+roll[2]]
                if self.state.def_blitz and self.state.def_blitz == r:
                    print_red("Rolled disabled cell, reroll!")
                    attempt = True
                    continue
                print(f'Offense rolled {roll}')
                res = self.playResults.getPlayResult(roll)
                
            elif play == "Attempt field goal (special scoring action)":
                cols = self.playResults.getFGCols()
                c = cols[-1]
                if self.state.yttd <= cols[0]: c = cols[0]
                elif self.state.yttd <= cols[1]: c = cols[1]
                r = [roll[0],c]
                if self.state.def_blitz and self.state.def_blitz == r:
                        print_red("Rolled disabled cell, reroll!")
                        attempt = True
                        continue
                roll = roll[:1]
                print(f'Offense rolled {roll}!')
                res = self.playResults.getFieldGoalResult(roll, self.state.yttd)
            elif "Punt" in play:
                r = [sum(roll)]
                if "Short" in play: 
                    roll = roll[:1]
                    r = roll
                else: roll = roll[:2]
                
                if self.state.def_blitz and self.state.def_blitz[0] == roll:
                    print_red("Rolled disabled cell, reroll!")
                    attempt = True
                    continue
                
                print(f'Offense rolled {roll}!')
                res = self.playResults.getPuntResult(roll)

            # give option to use TO if available on negative plays 
            #   or 3rd and 4th down, dont redo punts
            if self.state.getOffTimeouts() and \
                (res-self.state.ytfd < 0) and   \
                (res < 0 or self.state.down > 2) \
                and "Roll" in play:
                self.display_state()
                p = res
                if res == -100: p = "turnover"
                print_red(f'{self.offense.name} last play resulted in {p}')
                if self.offense.call_time_out(self.state, res) == "yes": 
                    attempt = True
                    self.state.time_outs[self.state.offense] -=1
                    print_yellow(f'{self.offense} is replaying the down using a timeout')
        
        self.evaluate_play(res)

    def evaluate_play(self, res:int):
        # returns a game state object that has the result of the play
        play = self.state.off_play_call
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
                elif res <= 0: print_red(f'{res} yard gain')
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
                
        elif "Punt" in play:
            # calculate new position of ball after punt
            new_pos = self.state.yttd - res
            if res == 0: print('Blocked punt!')
            elif new_pos <= 1:
                # punt went into endzone
                print_red(f'The punt went for {res} and into the endzone, touchback!')
                new_pos=80
                self.change_possesion(new_pos)
            else: 
                print_yellow(f'{self.offense} punted the ball {res} yards')
                self.doKickReturn(100 - new_pos)
                
        elif "goal" in play:
            if res: 
                # fg good, add 3 points and do kickoff
                print_green("Field Goal attempt is good!")
                self.state.scores[self.state.offense] += 3
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
                print_red("Touchback, the ball will be place at the 20")
                start = 80
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
                self.state.yttd = start
                self.state.ytfd = 10 if self.state.yttd > 10 else self.state.yttd
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
            self.change_possesion(start)
            
    def onsideKick(self):
        # roll 3 dice and must get the following results
        # d1 = 1,2,3
        # d2 and d3 = 5,6
        # returns TRUE for success, FALSE for fail
        roll = roll_3_d6()
        print_yellow(f"{self.offense} rolled {roll}")
        return (roll[0] < 4) and  (roll[1] > 4) and  (roll[2] > 4)
    
    def change_possesion(self, new_pos:int):
        # change game state to swap offense and defense roles
        # input: new_pos    new ball spot [1,99]
        self.state.change_possesion(new_pos)
        if self.state.offense == 1: 
            self.offense = self.p2
            self.defense = self.p1
        else: 
            self.offense = self.p1
            self.defense = self.p2
        print(f"{self.offense} is now on offense at the {self.state.yttd}, 1st and {self.state.ytfd}!")
            
if __name__ == "__main__":
     p1 = UserPlayer("Brad", 0)
     p2 = UserPlayer("Sav", 1)
     game = FootballDice(p1, p2, possessions=6)
