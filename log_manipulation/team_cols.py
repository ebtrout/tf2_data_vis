import pandas as pd
import numpy as np
from pandas import json_normalize

# Add extra columns to team_cols

def midfight_conversion(rounds,teams):
## Midfight Conversion ##
    # region Midfight Conversion
    converted = pd.Series([0,0],index = ["Red","Blue"],name = 'count')
    for i in range(0,len(rounds)):
        if rounds.loc[i,'winner'] == rounds.loc[i,'firstcap']:
            if rounds.loc[i,'winner'] == "Blue":
                converted["Blue"] = converted["Blue"] + 1
            else:
                converted["Red"] = converted["Red"] + 1

    firstcaps = rounds['firstcap'].value_counts().replace(0,np.nan)

    midpoint_convert = pd.Series(converted.div(firstcaps), name = "midfight_conversion").reset_index().rename(columns= {"index":"team"})


    teams = teams.merge(midpoint_convert,on = "team",how = "left")
    return teams

def counting_stats(teams,players):
        
        teams_temp = teams.copy()
        
        # Making team_deaths and team_assists bc its bugged
        team_stats = players.groupby("team").agg(
            team_deaths = ("deaths","sum"),
            team_assists = ("assists","sum"),
            team_dt = ('dt',"sum"),
            team_dt_real = ('dt_real','sum'),
            team_dmg_real = ('dmg_real','sum'),
            team_hr = ('hr','sum'),
            team_kills = ('kills','sum')
        ).reset_index()



        teams_temp = teams_temp.merge(team_stats)
        teams_temp['team_ka'] = teams_temp['team_kills'] + teams_temp['team_assists']
    
        teams_temp.columns = [col.replace("team_","") for col in teams_temp.columns]


        teams_temp = teams_temp[[col for col in teams_temp.columns if col not in teams.columns] + ['team']]

        teams = teams.merge(teams_temp,how = "left")

        teams['deaths'] = team_stats['team_deaths']

        return teams

def round_length(rounds,teams):

    # Average win length

    win_length = rounds.groupby('winner').agg(av_win_length = ("length","mean")).reset_index().rename(columns={'winner':"team"})

    teams = teams.merge(win_length,how = 'left')

    # Longest win
    longest_win = rounds.sort_values(by = 'length',ascending= False).groupby('winner').first()['length'].reset_index().rename(columns={'winner':"team",'length':"longest_win"})
    teams = teams.merge(longest_win,how = 'left')

    # Shortest win
    longest_win = rounds.sort_values(by = 'length',ascending= False).groupby('winner').last()['length'].reset_index().rename(columns={'winner':"team",'length':"shortest_win"})
    teams = teams.merge(longest_win,how = 'left')

    return teams

def winner(teams):
     ## TEAM WINNER ##
    # Look at score to see what team won
    if len(teams) > 0:
        team_winner = teams.loc[teams['score'] == teams['score'].max(),'team'].values[0]

        teams['winner'] = 0
        for i in teams['team']:
            if i == team_winner:
                teams.loc[teams['team'] == i, 'winner'] = 1
    else:
        teams['winner'] = pd.Series(dtype = 'int')
        
    return teams
