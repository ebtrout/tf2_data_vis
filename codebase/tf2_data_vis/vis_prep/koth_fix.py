import pandas as pd
import os
import numpy as np
def koth_matches(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'info.csv')
    info = pd.read_csv(path)

    koth = info.copy()
    koth = info[info['map'].str.split("_").str[0].str.contains("koth")]
    koth_count = koth['map'].str.lower().str.split("_")
    koth_count = pd.Series(koth_count.str[1].value_counts())
    koth_count = koth_count[koth_count > 20]
    koth_maps = koth_count.index.values
    koth_matches = info[info['clean_map_name'].isin(koth_maps)].copy()
    return koth_matches

def koth_stats(parent_dir,output_dir,koth_matches):
    path = os.path.join(parent_dir,'..',output_dir,'round_events.csv')
    round_events = pd.read_csv(path)

    point_caps = round_events[
        (round_events['type'] == 'pointcap') | (round_events['type'] == 'round_win')
    ].copy()

    match_round_list = []

    for i,match_id in enumerate(koth_matches['id'].unique()):
        if i % 100 == 0 and i != 0:
            print(f'Manipulated {i} / {koth_matches['id'].nunique()} koth matches')
        df = point_caps[point_caps['id'] == match_id].copy()

        for round_num in df['round'].unique():
            match_round = df[df['round'] == round_num].copy()

            # Compute lag_time and time_elapsed per group (team) using shift(-1)
            match_round['lag_time'] = match_round.groupby('team')['time'].shift(-1)
            match_round['time_elapsed'] = match_round['lag_time'] - match_round['time']
            match_round['time_elapsed'] = match_round['time_elapsed'].fillna(0)

            # Calculate total cap time per round and team
            cap_time_df = match_round.groupby(['round', 'team'])['time_elapsed'].sum().reset_index()
            cap_time_df.rename(columns={'time_elapsed': 'cap_time'}, inplace=True)
            match_round = match_round.merge(cap_time_df, on=['round', 'team'], how='left')

            # Number of caps per round and team
            num_caps = match_round[match_round['type'] == 'pointcap'].groupby(['round', 'team']).size().reset_index(name='num_caps')
            match_round = match_round.merge(num_caps, on=['round', 'team'], how='left')
            match_round['num_caps'] = match_round['num_caps'].fillna(0).astype(int)

            # Rolling cap times per team (cumulative sum of time_elapsed per team)
            match_round['blue_cap_time'] = match_round.apply(lambda row: row['time_elapsed'] if row['team'] == 'Blue' else 0, axis=1).cumsum()
            match_round['red_cap_time'] = match_round.apply(lambda row: row['time_elapsed'] if row['team'] == 'Red' else 0, axis=1).cumsum()

            # Winner for the round
            winners = match_round.loc[match_round['type'] == 'round_win', 'team']
            winner = winners.values[0] if not winners.empty else np.nan
            match_round['winner'] = winner

            # Roll condition
            red_cap_sum = match_round['red_cap_time'].sum()
            blue_cap_sum = match_round['blue_cap_time'].sum()
            if red_cap_sum == 0 and winner == 'Blue':
                match_round['roll'] = 1
            elif blue_cap_sum == 0 and winner == 'Red':
                match_round['roll'] = 1
            else:
                match_round['roll'] = 0

            # Comeback condition
            cond1 = (match_round['winner'] == 'Red') & (match_round['red_cap_time'] == 0) & (match_round['blue_cap_time'] >= 150)
            cond2 = (match_round['winner'] == 'Blue') & (match_round['blue_cap_time'] == 0) & (match_round['red_cap_time'] >= 150)
            if (cond1 | cond2).any():
                match_round['comeback'] = 1
            else:
                match_round['comeback'] = 0

            match_round_list.append(match_round)

    koth_stats = pd.concat(match_round_list)
    path = os.path.join(parent_dir,'..',output_dir,'koth_stats.csv')
    koth_stats.to_csv(path,index = False)

def koth_rounds(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'koth_stats.csv')
    koth_stats_df = pd.read_csv(path)

    path = os.path.join(parent_dir,'..',output_dir,'rounds.csv')
    rounds = pd.read_csv(path)


    # Lead changes
    koth_stats_df['blue_cap_time_lag'] = koth_stats_df['blue_cap_time'].shift(1).fillna(0)
    koth_stats_df['red_cap_time_lag'] = koth_stats_df['red_cap_time'].shift(1).fillna(0)


    koth_stats_df['leader'] = np.where(
        koth_stats_df['blue_cap_time'] > koth_stats_df['red_cap_time'], 'Blue',
        np.where(koth_stats_df['blue_cap_time'] < koth_stats_df['red_cap_time'], 'Red', "")
    )

    koth_stats_df['leader_lag'] = np.where(
        koth_stats_df['blue_cap_time_lag'] > koth_stats_df['red_cap_time_lag'], 'Blue',
        np.where(koth_stats_df['blue_cap_time_lag'] < koth_stats_df['red_cap_time_lag'], 'Red', "")
    )

    lead_changes_long = koth_stats_df[(koth_stats_df['leader'] != koth_stats_df['leader_lag'])
                & (koth_stats_df['leader'] != "")
                & (koth_stats_df['leader_lag'] != "")].copy()

    lead_changes_long['blue_lead_change'] = np.where(lead_changes_long['leader'] == 'Red',1,0)
    lead_changes_long['red_lead_change'] = np.where(lead_changes_long['leader'] == 'Blue',1,0)

    lead_changes = lead_changes_long.groupby(['id','round'])[['blue_lead_change','red_lead_change']].sum().reset_index()

    koth_group = koth_stats_df.groupby(['id','round'])

    comeback = koth_group.first()['comeback'].reset_index()

    roll = koth_group.first()['roll'].reset_index().drop(['id','round'],axis = 1)

    num_caps = koth_group.first()['num_caps'].reset_index().drop(['id','round'],axis = 1)


    koth_rounds = pd.concat([comeback,roll,num_caps],axis =1)
    koth_rounds = koth_rounds.merge(rounds[['id','round','firstcap','length','winner']],on = ['id','round'])
    koth_rounds = koth_rounds.merge(lead_changes,on = ['id','round'],how = 'left')
    path = os.path.join(parent_dir,'..',output_dir,'koth_rounds.csv')
    koth_rounds.to_csv(path,index = False)

def make_is_koth(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'koth_rounds.csv')
    koth_rounds = pd.read_csv(path)
    koth_rounds['is_koth'] = np.where(koth_rounds['winner'].isna(),0,1)
    is_koth_df = koth_rounds[['id','is_koth']]
    is_koth_df = is_koth_df.groupby('id').first().reset_index()
    path = os.path.join(parent_dir,'..',output_dir,'is_koth.csv')
    is_koth_df.to_csv(path,index = False)






