import pandas as pd
import numpy as np
from pandas import json_normalize

## POST UBER EVENTS
def post_uber(round_events, team_medic_stats, players,
              exchange_width,success_width,
              medic_death_width,medic_death_capitalize_window,
              round_losing_medic_death_window,
              drops_forced_width):
    
    invert_team = pd.Series(["Red", "Blue"], index=['Blue', 'Red'])

    # region POST UBER EVENTS

    charge_stats = round_events[round_events['type'] == 'charge'].reset_index()

    exchanges_initiated = pd.Series([0,0],index = ["Red",'Blue'],name = "exchanges_initiated")

    drops_forced = pd.Series([0,0],index = ["Red",'Blue'],name = "drops_forced")

    successful_ubers = pd.Series([0,0],index = ["Red",'Blue'],name = "successful_ubers")

    medic_deaths_forced = pd.Series([0,0],index = ["Red",'Blue'],name = "medic_deaths_forced")

    for i in range(0,len(charge_stats)):
        team = charge_stats.loc[i,'team']
        time = charge_stats.loc[i,'time']

        # Medic Forces / Forced Drops #

        events = round_events[(round_events['time'] > time) & (round_events['time'] <= time + exchange_width)]
        events = events[~((events['type'] == 'charge') & (events['team'] == team))]
        
        if 'charge' in events['type'].values:
            exchanges_initiated[team] += 1

        # Successful Uber Pushes #
        events = round_events[(round_events['time'] > time) & (round_events['time'] <= time + success_width)]
        events = events[events['type'] == 'pointcap']

        # Check if any point is capped
        if len(events) != 0:
        # Check if the first cap within the width of the uber is for the ubering team
            first_cap_team = events.groupby('type').first()['team'].values[0]
            if first_cap_team == team:
                successful_ubers[team] += 1
        
        # Medic Deaths Forced
        events = round_events[(round_events['time'] > time) & (round_events['time'] <= time + medic_death_width)]
        events = events[(events['team'] != team)]
        events = events[(events['type'] == "medic_death")]
        # Check if there is an event that matches
        if len(events) != 0:
            medic_deaths_forced[team] += 1
        # Drops Forced
        events = round_events[(round_events['time'] > time) & (round_events['time'] <= time + drops_forced_width)]
        events = events[(events['team'] != team)]
        events = events[(events['type'] == "drop")]
        # Check if there is an event that matches
        if len(events) != 0:
            drops_forced[team] += 1

    ## MAKE ALL THE STATS INTO RATES AND BIND THEM IN TO MEDIC STATS!!!!!!!

    uber_stats = pd.concat(
        [exchanges_initiated, drops_forced, successful_ubers, medic_deaths_forced],
        axis=1
    ).reset_index().rename(columns={"index":"team"})

    player_deaths = players.groupby(['team','primary_class']).agg(medic_deaths = ("deaths","sum")).reset_index()
    medic_deaths = player_deaths[player_deaths['primary_class'] == 'medic'].drop('primary_class',axis=1)

    team_medic_stats = team_medic_stats.merge(medic_deaths,how = 'left')

    uber_stats['exchanges_not_initiated'] = uber_stats['exchanges_initiated'].values[::-1]

    team_medic_stats = team_medic_stats.merge(uber_stats,how = 'left')

    team_medic_stats = team_medic_stats.replace(0,np.nan)

    team_medic_stats['successful_uber_rate'] = team_medic_stats['successful_ubers'].div(team_medic_stats['ubers']).astype(float).round(4)

    team_medic_stats['exchanges_initiated'] = team_medic_stats['exchanges_initiated'].div(team_medic_stats['ubers']).astype(float).round(4)

    invert_medic_deaths_forced = pd.Series(team_medic_stats['medic_deaths_forced'].values[::-1])

    team_medic_stats['forced_medic_death_rate'] = invert_medic_deaths_forced.div(team_medic_stats['medic_deaths']).astype(float).round(4)

    invert_drops_forced = pd.Series(team_medic_stats['drops_forced'].values[::-1])

    team_medic_stats['forced_drop_rate'] = invert_drops_forced.div(team_medic_stats['drops']).astype(float).round(4)
    # endregion

    ## POST MEDIC DEATH EVENTS
    # region POST MEDIC DEATH EVENTS 

    medic_deaths_capitalized = pd.Series([0,0],index = ["Red",'Blue'],name = "medic_deaths_capitalized")

    round_losing_medic_deaths = pd.Series([0,0],index = ["Red",'Blue'],name = "round_losing_medic_deaths")


    medic_death_stats = round_events[round_events['type'].isin(['medic_death','drop'])].reset_index()
    for i in range(0,len(medic_death_stats)):
        team = medic_death_stats.loc[i,'team']
        time = medic_death_stats.loc[i,'time']
        
        # Deaths Capitalized

        events = round_events[(round_events['time'] > time) & (round_events['time'] <= time + medic_death_capitalize_window)]
        events = events[((events['type'] == 'pointcap') & (events['team'] != team))]
        
        if len(events) != 0:
            medic_deaths_capitalized[invert_team[team]] += 1
        
        # Round losing med deaths
        events = round_events[(round_events['time'] > time) & (round_events['time'] <= time + round_losing_medic_death_window)]
        events = events[((events['type'] == 'round_win') & (events['team'] != team))]
        
        if len(events) != 0:
            round_losing_medic_deaths[invert_team[team]] += 1


    #  Binding in to team_medic_stats
    medic_death_stats = pd.concat(
        [medic_deaths_capitalized,round_losing_medic_deaths],axis = 1
    ).reset_index().rename(columns={"index":"team"})

    team_medic_stats = team_medic_stats.merge(medic_death_stats,how = 'left')

    team_medic_stats['round_losing_medic_death_rate'] = team_medic_stats['round_losing_medic_deaths'].div(
        team_medic_stats['medic_deaths']
    ).astype(float).round(4)

    invert_medic_deaths = team_medic_stats['medic_deaths'].values[::-1]

    team_medic_stats['medic_death_capitalization_rate'] = team_medic_stats['medic_deaths_capitalized'].div(
        invert_medic_deaths
    ).astype(float).round(4)

    return team_medic_stats

def additional_rates(rounds,players,team_medic_stats):
    num_rounds = len(rounds)

    team_medic_stats['advantages_lost_per_round'] = team_medic_stats['medicstats.advantages_lost'].div(num_rounds).astype(float).round(4)

    medic_time = players[players['primary_class'] =='medic'][['team','primary_class_time']]

    team_medic_stats = team_medic_stats.merge(medic_time)

    team_medic_stats['mins'] = team_medic_stats['primary_class_time'].div(60)

    team_medic_stats['uberspm'] = team_medic_stats['ubers'].div(team_medic_stats['mins']).astype(float).round(4)

    team_medic_stats.drop(['mins','primary_class_time'],axis = 1,inplace = True)

    return(team_medic_stats)
