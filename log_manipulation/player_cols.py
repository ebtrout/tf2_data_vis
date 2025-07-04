import pandas as pd
import numpy as np
from pandas import json_normalize

# Add extra stats to the players datasets

## REQUIRES PLAYERS ##
def names(log,players):
    ## NAMES ##
    df = pd.DataFrame.from_dict(log['names'], orient='index')
    df = df.reset_index().rename(columns={'index':'steamid',0:'name'})

    players = pd.concat([df['name'],players],axis = 1)
    return players

## REQUIRES CLASS_STATS and PLAYERS ##
def primary_class(class_stats,players):
## Primary Class ## 
    class_stats.sort_values(by = ['steamid','total_time'],ascending= False, inplace=True)
    primary_class = class_stats.groupby('steamid').first().reset_index()[['steamid', 'type','total_time']]

    primary_class.rename(columns={'type': 'primary_class','total_time':'primary_class_time'}, inplace=True)

    players = primary_class.merge(players, on='steamid', how='left')

    return players

def offclass(class_stats,players):
## Percent time offclassing ##

    primary_class = class_stats.groupby("steamid").first().replace(0,np.nan)

    primary_class['offclass_time'] = primary_class['total_time'] - primary_class['class_time']

    primary_class['offclass_pct'] =( primary_class['offclass_time'].div(primary_class['total_time'])).astype(float).round(4)

    primary_class.reset_index(inplace=True)

    primary_class = primary_class[['steamid','offclass_time','offclass_pct',"total_time"]]

    players = players.merge(primary_class,on = "steamid",how = "right")

    return players

## Player Match Averages ##
def player_percentages(teams,players):
    # region Player Match Averages

    # Make Team Stats
    teams_temp = teams.copy()

    drop_cols = ['firstcaps','score','midfight_conversion','drops','charges','deaths']
    drop_cols = [col for col in drop_cols if col in teams_temp.columns]
    teams_temp.drop(drop_cols,axis = 1,inplace = True)
    teams_temp.columns = ["team"] + ["team_" + col for col in teams_temp.columns if col != "team"]

    # Making team_deaths and team_assists bc its bugged
    team_stats = players.groupby("team").agg(
        team_deaths = ("deaths","sum"),
        team_assists = ("assists","sum"),
        team_dt = ('dt',"sum"),
        team_dt_real = ('dt_real','sum'),
        team_dmg_real = ('dmg_real','sum'),
        team_hr = ('hr','sum')
        ).reset_index()
    teams_temp = teams_temp.merge(team_stats)
    teams_temp['team_ka'] = teams_temp['team_kills'] + teams_temp['team_assists']

    # Make player avs
    player_av_temp = players.merge(teams_temp,on = "team").replace(0,np.nan)
    player_av = pd.DataFrame()
    player_av['kill_pct']       = player_av_temp['kills'].div(player_av_temp['team_kills']).astype(float)
    player_av['deaths_pct']     = player_av_temp['deaths'].div(player_av_temp['team_deaths']).astype(float)
    player_av['dmg_pct']        = player_av_temp['dmg'].div(player_av_temp['team_dmg']).astype(float)
    player_av['dmg_real_pct']   = player_av_temp['dmg_real'].div(player_av_temp['team_dmg_real']).astype(float)
    player_av['cpc_pct']        = player_av_temp['cpc'].div(player_av_temp['team_caps']).astype(float)
    player_av['ka_pct']         = player_av_temp['ka'].div(player_av_temp['team_ka']).astype(float)
    player_av['assists_pct']    = player_av_temp['assists'].div(player_av_temp['team_assists']).astype(float)
    player_av['dt_pct']         = player_av_temp['dt'].div(player_av_temp['team_dt']).astype(float)
    player_av['dt_real_pct']    = player_av_temp['dt_real'].div(player_av_temp['team_dt_real']).astype(float)
    player_av['hr_pct']         = player_av_temp['hr'].div(player_av_temp['team_hr']).astype(float)


    # Round and add steamid
    player_av = player_av.round(4)
    player_av['steamid'] = player_av_temp['steamid']

    # Merge
    players = players.merge(player_av,on = "steamid")
    return players

def player_per_death(players):
    # ASSISTS
    players['assistspd'] = players['assists'] / players['deaths']

def players_per_minute(players):
    # DT
    # Deaths
    # CPC
    # healps
    # medkit_hp

    minutes = (1 / (players['dapm']) ) * players['dmg']

    cols = ['heal','dt','dt_real','cpc','medkits_hp']

    for col in cols:
        name = col + "pm"
        players[name] = (players[col] / minutes).astype(float).round(4)

def hroi(players):
    ## HROI
    # region HROI

    players = players.replace(0,np.nan)
    players['hroi'] = players['dmg'].div(players['hr'])
    players['hroi_real'] = players['dmg_real'].div(players['hr'])

    return players

def suicide_rate(players):
    ## Suicide Rate ##

    players['suicide_rate'] = players['suicides'].div(players['deaths']).astype(float).round(4)
    return(players)