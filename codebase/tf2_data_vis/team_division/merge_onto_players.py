import pandas as pd
import numpy as np
from .steamid import convert_steamid

def make_team_divison(players,sixes_teams,info):
    player_divisions_no_weight = make_player_divisions(players,sixes_teams,info)
    player_divisions = map_division_to_weight(player_divisions_no_weight)
    team_divisions = player_divisions.groupby(['id','team'])['division_weight'].mean()
    team_divisions = team_divisions.fillna(1).reset_index()
    return team_divisions

def make_player_divisions(players,sixes_teams,info):
    players['steamid64'] = players['steamid'].apply(convert_steamid)
    sixes_teams['steamid64'] = sixes_teams['steamid'].copy()

    # Turn whe player left and joined to datetime
    sixes_teams['startedAt'] = pd.to_datetime(sixes_teams['startedAt']).dt.tz_localize(None)
    sixes_teams['leftAt'] = pd.to_datetime(sixes_teams['leftAt']).dt.tz_localize(None)
    sixes_teams['leftAt'] = sixes_teams['leftAt'].fillna(pd.Timestamp.now())

    # Many to many match players 
    player_teams = players.merge(sixes_teams,on = 'steamid64',how = 'inner')
    player_teams = player_teams.merge(info[['id','date']],on = 'id')
    player_teams['date'] = pd.to_datetime(player_teams['date'])

    # Calculate how long it has been from the logs.tf log date and the time they left / joined the team
    player_teams['near_start'] = (player_teams['date'] - player_teams['startedAt']).dt.total_seconds().abs() / (60 * 60 * 24)
    player_teams['near_left'] = (player_teams['date'] - player_teams['leftAt']).dt.total_seconds().abs() / (60 * 60 * 24)

    # Find the closest team
    closest_team = player_teams.groupby(['id','steamid64']).agg(
        near_start_idx=('near_start', 'idxmin'),
        near_left_idx=('near_left', 'idxmin'),
        near_start_min=('near_start', 'min'),
        near_left_min=('near_left', 'min')
    ).reset_index()

    divisions =  player_teams.loc[closest_team['near_start_idx'],'divisionName'].copy()

    closest_team['division'] = divisions.values

    player_divisions = players.merge(closest_team[['id','steamid64','division']],on = ['id','steamid64'],how = 'left')
    return player_divisions

def map_division_to_weight(player_divisions):
    player_divisions = player_divisions.copy()
    player_divisions['division'] = player_divisions['division'].fillna('NA')
    division_weights ={
        "NA":np.nan,
        "newcomer":1,
        'amateur':1.5,
        'intermediate':2,
        'main':3,
        'advanced':5,
        'invite': 10
    }

    player_divisions['division_weight'] = player_divisions['division'].map(division_weights)
    return player_divisions




