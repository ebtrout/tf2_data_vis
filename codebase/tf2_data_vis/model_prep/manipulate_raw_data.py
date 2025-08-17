import pandas as pd
import os
import numpy as np

def read_data(parent_dir,output_dir):
    data_dict = {}
    for f in ['players','info','team_medic_stats','teams']:
        path = os.path.join(parent_dir,'..',output_dir,f + '.csv')
        df = pd.read_csv(path)
        data_dict[f] = df
    return data_dict

# Test if there are 1 demo 2 scout 2 solider 1 med
def team_class_comp(players: pd.DataFrame):
        
    team_comp = players.groupby(['id', 'team'])['primary_class'].agg(lambda x: ".".join(x)).reset_index(name='class_concat')

    team_comps = (team_comp['class_concat'].str.split("."))

    # Test if team_comp is correct
    correct = []
    for team in team_comps:
        if len(team) != 6:
            correct.append(0)
            continue
        demoman = 0
        soldier = 0 
        scout = 0
        medic = 0
        for class_name in team:
            if class_name == 'demoman':
                demoman += 1
            if class_name == 'soldier':
                soldier += 1
            if class_name == 'scout':
                scout += 1
            if class_name == 'medic':
                medic += 1
        if demoman == 1 and soldier == 2 and scout == 2 and medic == 1:
            correct.append(1)
        else:
            correct.append(0)

    team_comp['correct'] = correct

    team_comp = team_comp.groupby('id').agg(correct_team_comp = ('correct','sum'))

    team_comp = team_comp[team_comp['correct_team_comp'] == 2]

    players_team_comp = players[players['id'].isin(team_comp.reset_index()['id'])].copy()

    return players_team_comp

def short_matches(info,player_team_comp,short_match_cutoff = 450):
    info_team_comp = info[info['id'].isin(player_team_comp['id'].values)]

    short_matches = info_team_comp[info_team_comp['length'] < short_match_cutoff]
    players_subset = player_team_comp[~player_team_comp['id'].isin(short_matches['id'])].copy()
    return players_subset


def rename_scout_soldier(players_subset):
    players_fixed_class_names = players_subset.copy()
    players_scout_soldier = players_fixed_class_names[players_fixed_class_names['primary_class'].isin(['scout','soldier'])]
    players_medic_demo = players_fixed_class_names[~players_fixed_class_names['primary_class'].isin(['scout','soldier'])]
    df = players_scout_soldier.copy()

    # Step 1 — Find max hr_pct in each group
    group_cols = ['id', 'team', 'primary_class']
    df['max_hr_pct'] = df.groupby(group_cols)['hr_pct'].transform('max')
    df['min_hr_pct'] = df.groupby(group_cols)['hr_pct'].transform('min')

    # Find a classroll
    df['role'] = np.where( np.abs(df['hr_pct'] - df['max_hr_pct']) <= .0001,'pocket','roamer')

    # If multiple roles exist assign them randomly
    df['role_check'] = df.groupby(group_cols)['role'].transform('sum')

    df_bad = df[df['role_check'].isin(['roamerroamer','pocketpocket'])].copy()

    # Apply Function to randomly assign one 'pocket' and one 'roamer' per group
    df_bad = df_bad.groupby(['id','team','primary_class'], group_keys=False).apply(assign_roles_randomly,include_groups = False)

    # Put the results back into the original DataFrame
    df.update(df_bad)
    df['primary_class'] = df['primary_class'] + "_" + df['role']
    df.drop(['role','role_check','min_hr_pct','max_hr_pct'],axis = 1,inplace = True)

    # Concat
    players_scout_soldier = df
    players_fixed_class_names = pd.concat([players_medic_demo,players_scout_soldier])

    return players_fixed_class_names

# Function to randomly rename duplicate classes within each group
def assign_roles_randomly(group):
        idx = group.sample(2, random_state=np.random.randint(0, 1_000_000)).index
        group.loc[idx[0], 'role'] = 'pocket'
        group.loc[idx[1], 'role'] = 'roamer'
        return group


def split_combat_medic(players_fixed_class_names,team_medic_stats):
    drop_cols = drop_cols_list()
    drop_combat = drop_combat_list()
    drop_medic = drop_medic_list()

    players_fixed_class_names.drop(drop_cols,axis =1,inplace = True)

    combat_classes = ['scout', 'soldier', 'demoman']
    pattern = '|'.join(combat_classes)  # Creates 'scout|soldier|demoman'
    combat_players = players_fixed_class_names[players_fixed_class_names['primary_class'].str.contains(pattern, case=False, na=False)].copy()

    # Make medic stats
    medic_players = players_fixed_class_names[players_fixed_class_names['primary_class'] == 'medic'].copy()

    # Bind in team_medic
    medic_players = medic_players.merge(team_medic_stats,on= ['id','team'])

    # Drop Bad columns

    combat_players.drop(drop_combat,axis = 1,inplace = True)

    medic_players.drop(drop_medic,axis = 1,inplace = True)

    # Make columns numeric and fillna with 0
    non_numeric_columns = ['id', 'team', 'primary_class','steamid']
    for df in [medic_players,combat_players]:
        for col in df.columns:
                if col in non_numeric_columns:
                        continue
                df[col] = pd.to_numeric(df[col])

    # Remove medicstats. from colnames

    medic_players.columns = [col.replace("medicstats.","") for col in medic_players.columns]

    return medic_players,combat_players


def drop_medic_list():
    drop_medic = [
        'offclass_pct', 'hroi_real', 'hr_pct',
        'medicstats.advantages_lost', 'medicstats.deaths_with_95_99_uber',
        'medicstats.deaths_within_20s_after_uber', 'ubers', 'drops',
        'exchanges_initiated', 'drops_forced',
        'successful_ubers', 'medic_deaths_forced', 'exchanges_not_initiated',
        'successful_uber_rate', 'forced_medic_death_rate', 'forced_drop_rate',
        'medic_deaths_capitalized', 'round_losing_medic_deaths',
        'medic_death_capitalization_rate',
        'advantages_lost_per_round', 'round_losing_medic_death_rate',
        'exchanges_not_initiated_rate', 'exchanges_initiated_rate'
    ]
    return drop_medic


def drop_combat_list():
    drop_combat = ['healpm']
    return drop_combat

def drop_cols_list():
    drop_cols = [
        'primary_class_time', 'name',
        'assists', 'cpc', 'heal', 'hr', 'deaths', 'dmg', 'dmg_real', 'drops',
        'dt', 'dt_real', 'kills', 'medkits', 'medkits_hp', 'sentries',
        'suicides', 'ka', 'offclass_time', 'total_time', 'kapd', 'ka', 'ka_pct',
        'hroi', 'dmg_real_pct', 'dmg_pct', 'suicide_rate','kpd'
    ]
    return drop_cols

def widen_data(medic_players,combat_players):
    index_columns = ['id', 'team', 'primary_class']
    combat_wide = (
        combat_players
        .set_index(index_columns)  # MultiIndex
        .unstack('primary_class')                    # Pivot on class
    )

    medic_wide = (
        medic_players
        .set_index(index_columns)  # MultiIndex
        .unstack('primary_class')                        # Pivot on class
    )

    # Step 3: Flatten the MultiIndex column names
    combat_wide.columns = [f"{cls}_{stat}" for stat, cls in combat_wide.columns]

    # Step 4: Reset index
    combat_wide = combat_wide.reset_index()

    # Drop non-scout offclass 
    cols = [col for col in combat_wide.columns if 'offclass' in col and 'scout' not in col]
    combat_wide = combat_wide.drop(cols,axis = 1)

    # Step 3: Flatten the MultiIndex column names
    medic_wide.columns = [f"{cls}_{stat}" for stat, cls in medic_wide.columns]

    # Step 4: Reset index
    medic_wide = medic_wide.reset_index()

    return medic_wide,combat_wide


def merge_wide_data(medic_wide,combat_wide,teams):
    medic_merger = medic_wide.drop(['id','team'],axis =1)

    # Merge medic and combat
    players_wide = pd.concat([combat_wide,medic_merger],axis = 1)

    players_wide = players_wide.merge(teams[['id','team','winner']],on =['id','team'])
    
    return players_wide
