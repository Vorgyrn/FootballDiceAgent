# FootballDiceAgent
PSU AI 801 Group 8 Project

# Game simplifications
In order to make the game a little more simple for the agent to interact with (ie less decision nodes) some aspects of the game were simplified

## Offense
1. You cannot use a timeout on every play
    - keeps the game flowing at a better pace if time outs can only be used on roll attempts durring 3rd or 4th down or on negative plays
2. Two TO's (-100 on the results grid) in a row do not result in a turn over
   - I just didnt like this rule


## Defense
1. The defense does not get the choice to accept/decline penalties, infact there are not penalties just negative plays, therefore removing a decsion node from the game
2. blitzes can only be used to cross out values from the regular play stat chart, not the fg or punt charts
3. Kick returns are limited to 3 dice rolls, little value provided by adding another decision there

## Overtime
There is no overtime, the game just goes to sudden death, no expendables are added
