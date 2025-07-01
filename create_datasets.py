import pandas as pd
import numpy as np
import requests
from pandas import json_normalize
import joblib

## INFO ##
def info(log,id):
    map = log['info']['map']
    title = log['info']['title']
    length = log['length']
    date = log['info']['date']


    info = pd.DataFrame({'id': [id], 'length': [length], 'map': [map],'title':[title],'date':[date]})
    info['date'] = pd.to_datetime(info['date'], unit='s')
    # If Too Short Skip
    if length < 200:
        return(f'{log} Too Short. Only {length} seconds long')

    return(info)

def players(log):
    
    # Shape players to be usable
    players = json_normalize(log['players'])
    players = players.T
    players['stats'] = players[0]
    players.drop(columns=[0], inplace=True)
    players.reset_index(inplace=True)
    players[['steamid', 'metric']] = players['index'].str.extract(r'(\[U:1:\d+\])(?:\.(.*))?')

    # Drop where player steam id is NA
    players = players[players['steamid'].notna()]

    # Pivot so there are multiple columns per row
    players = players.pivot(index = 'steamid', columns='metric', values='stats')

    # Drop useless columns
    drop_cols = ['as','backstabs','headshots','headshots_hit','lks','ic']
    drop_cols = [col for col in drop_cols if col in players.columns]
    players.drop(drop_cols,axis = 1,inplace = True)

    # Create ka 
    for col in ['kills','assists']:
        if col not in players.columns:
            players[col] = pd.Series(dtype = 'int')
    
    players['ka'] = players['kills'] + players['assists']
    return(players)

## REQUIRES PLAYERS!! ##
def medic_stats(players):
    
    # Separate medic stats and player stats
    colnames = players.columns
    colnames = [col for col in colnames if "medi" not in col and "uber" not in col and "drops"]

    medic_stats = players[[col for col in players.columns if col not in colnames]]
    players = players[colnames]

    return(players,medic_stats)

## REQUIRES PLAYERS!! ##
def class_stats(players):

    # region Class Stats
    class_stats = pd.DataFrame()
    for i in range(0,len(players)):
        player_class =  pd.DataFrame(players.loc[players.index[i],'class_stats'])
        player_class = player_class[player_class['type'] != 'undefined']
        player_class['steamid'] = players.index[i]
        
        class_stats = pd.concat([class_stats, player_class], ignore_index=True)
        
    # Grab Weapon Stats
    #weapon = class_stats[['weapon','steamid','type']].copy()
    if 'weapon' in class_stats.columns:
        class_stats.drop('weapon',axis = 1,inplace = True)

    # Check if class_stats is null??
    if len(class_stats) > 0:
        class_stats = class_stats[['steamid'] + [col for col in class_stats.columns if col != 'steamid']]

        class_stats['total_time'] = class_stats['total_time'].abs()

        time_alive = class_stats.groupby('steamid').agg(time = ("total_time","sum")).reset_index()

        class_stats = class_stats.merge(time_alive)

        class_stats.rename(columns = {'time':'total_time',"total_time":"class_time"},inplace = True)

        # Drop the 'class_stats' column from players DataFrame
        players.drop('class_stats',axis = 1,inplace = True)
    return players, class_stats

def teams(log):
    ## TEAMS ## 

    # Shape teams
    teams = json_normalize(log['teams']).T.reset_index()
    teams[['team','metric']] = teams['index'].str.extract(r'(\w+)(?:\.(.*))?')
    teams.drop(columns=['index'], inplace=True)

    # Pivot to have multiple cols
    teams = teams.pivot(index='team', columns='metric', values=0)
    teams = teams.replace(0,np.nan)

    # Make drop_rate
    teams['drop_rate'] = teams['drops'].div(teams['charges']).astype(float).round(4)
    teams.reset_index(inplace = True)

    return teams

