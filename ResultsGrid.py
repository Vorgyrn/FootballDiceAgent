import pandas as pd

# non standard play results are as follows
# 100 == TOUCHDOWN
# -100 == TURNOVER
# X# cells are can be randomly generated or set to a preset value at the beginning of the game, provides a bit of a change 

default_x = {"X1":13, "X2":-5, "X3":0 }
class ResultsGrid:
    def __init__(self, plays="grids/plays.csv", field_goals="grids/field_goals.csv", punt="grids/punt.csv", xvals=default_x):
        self.plays = pd.read_csv(plays).replace(xvals).rename(columns=int).astype(int)
        self.plays.index += 1
        
        self.field_goals = pd.read_csv(field_goals).rename(columns=int).astype(int)
        self.field_goals.index += 1
        
        self.punt = pd.read_csv(punt).rename(columns=int).astype(int)
        self.punt.index += 1

        self.useTempGrid = False

    # play result functions
    def getPlayResult(self, roll:list):
        # determines the result of an offensive play
        # input: roll   a list of 1-3 dice roll results
        # output:       a result from the dice grid, all results relative to progress towards defenses endzone
        # -100          turnover!
        # [-99,-1]      negative movement of the ball
        # [0,99]        forward movement of the ball
        # 100           touchdown!
        playFuncs = {
                1:self._get1DicePlayResult,
                2:self._get2DicePlayResult,
                3:self._get3DicePlayResult
            }
        
        return playFuncs[len(roll)](*roll)

    def _get1DicePlayResult(self, d1):
        # result from rolling the special action from being within the 5 yard 
        # line. Always uses the first column
        # input: d1     the row select
        # output:       a result from the dice grid, all results relative to progress towards defenses endzone
        # -100          turnover!
        # [-99,-1]      negative movement of the ball
        # [0,99]        forward movement of the ball
        # 100           touchdown!
        return self.plays.at[d1, 1]
    
    def _get2DicePlayResult(self, d1, d2):
        # consult play result grid for result of rolling 2 dice
        # input: d1     the row select
        # input: d2     the column select (only 1-6)   
        # output:       a result from the dice grid, all results relative to progress towards defenses endzone
        # -100          turnover!
        # [-99,-1]      negative movement of the ball
        # [0,99]        forward movement of the ball
        # 100           touchdown!
        return self.plays.at[d1, d2]

    def _get3DicePlayResult(self, d1, d2, d3):
        # consult play result grid for result of rolling 3 dice
        # input: d1     the row select
        # input: d2     half of the column select
        # input: d3     other half of the column select  
        # output:       a result from the dice grid, all results relative to progress towards defenses endzone
        # -100          turnover!
        # [-99,-1]      negative movement of the ball
        # [0,99]        forward movement of the ball
        # 100           touchdown!
        return self.plays.at[d1, d2+d3]
    
    def getPuntResult(self, roll:list):
        # consult punt result grid for result of the punt
        # input: roll   a list with dice roll results (1 or 2 dice)
        # output:       distance the punt went, 0 - 65 yards
        return self.punt.at[1, sum(roll)]
    
    def getFieldGoalResult(self, roll:list, dist:int):
        # determine if the field goal attempt was succesful 
        # based on the roll and distance 
        # input: roll       list of dice rolls, the first value 
        #                   in the list is always used here
        # input: dist       distance of the field goal attempt
        # returns:          True for success, False for miss
        
        if dist <= self.field_goals.columns[0]:
            # field goal is within "close" distance
            dist = self.field_goals.columns[0]
        elif dist <= self.field_goals.columns[1]:
            # field goal is within "middle" distance
            dist = self.field_goals.columns[1]
        else:
            # field goal is within "far" distance
            dist = self.field_goals.columns[2]
        return bool(self.field_goals.at[roll[0], dist])

    def get2PointResult(self, roll:list):
        # check if the 2 point conversion attempt was good
        # input: roll       list of dice rolls, the first value in the list is always used here
        # return:           True if successfull, False otherwise
        d1 = roll[0]
        return (d1 % 2) == 0

    def setTempValue(self, row,col,val):
        self.useTempGrid = True
    
    def getPlayRow(self, row):
        return self.plays.loc[row]        

if __name__ == "__main__":
    resGrid = ResultsGrid()

    print(resGrid.getFieldGoalResult([1,2], 43))
    print(resGrid.getPlayResult([6,5,4]))
    print(resGrid.getPuntResult([2, 6]))
    
    
    