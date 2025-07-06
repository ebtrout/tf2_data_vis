import pandas as pd
import numpy as np
import joblib
import random
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
pd.set_option('future.no_silent_downcasting', True)
data = joblib.load("../data/pkls/df_dict.pkl")

short_match_cutoff = 450

min_map_play_count = 50

drop_cols = [ 'primary_class_time', 'name',
       'assists', 'cpc','heal', 'hr','deaths', 'dmg', 'dmg_real', 'drops',
       'dt', 'dt_real','kills','medkits','medkits_hp','sentries', 
       'suicides','ka','offclass_time','total_time','kapd','ka','ka_pct','hroi',"dmg_real_pct",
       "dmg_pct"]

drop_medic = ['offclass_pct','hroi_real','hr_pct',
              'medicstats.advantages_lost','medicstats.deaths_with_95_99_uber',
       'medicstats.deaths_within_20s_after_uber', 'ubers', 'drops',
       'medic_deaths', 'exchanges_initiated', 'drops_forced',
       'successful_ubers', 'medic_deaths_forced', 'exchanges_not_initiated',
       'successful_uber_rate', 'forced_medic_death_rate', 'forced_drop_rate',
       'medic_deaths_capitalized', 'round_losing_medic_deaths',
        'medic_death_capitalization_rate',
       'advantages_lost_per_round']

drop_combat = ['healpm']

unimportant_columns = ['soldier_dt_real_pct_2', 'medic_healpm', 'soldier_hrpm_1',
       'medic_hrpm', 'scout_dt_real_pct_1', 'soldier_dt_pct_2',
       'scout_hrpm_2', 'medic_deaths_within_20s_after_uber_rate',
       'demoman_deaths_pct', 'soldier_deaths_pct_1',
       'soldier_assists_pct_1', 'scout_dt_pct_2', 'medic_dt_pct',
       'medic_kill_pct', 'demoman_dt_real_pct', 'soldier_hr_pct_2',
       'scout_assists_pct_1', 'medic_avg_time_before_using',
       'soldier_dt_realpm_2', 'soldier_hrpm_2', 'scout_medkits_hppm_1',
       'medic_assists_pct', 'scout_hr_pct_1', 'demoman_hrpm',
       'medic_dapm']

### SETUP ###
# region SETUP
# Load necessary data

players = data['players']
teams = data['teams']
team_medic_stats = data['team_medic_stats']
info = data['info']
class_kda = data['class_kda']
# endregion

## Limit to only 1 med 1 demo 2 scout 2 soldier teams
# region CORRECT TEAM COMP
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

players = players[players['id'].isin(team_comp.reset_index()['id'])]

# endregion

# Drop short matches
# region DROP SHORT MATCHES
short_matches = info[info['length'] < short_match_cutoff]
players = players[~players['id'].isin(short_matches['id'])]

# endregion

# Valid Maps
## Check if map is valid
# If the map doesnt have at least 50 plays, not valid.
# Sometimes people just upload as "sunshine" need to ensure there are only single maps

# region MAPS

# Find valid map names
info_correct = info[info['id'].isin(players['id'])].copy()
maps = info_correct['map'].str.lower().str.split("_")
map_counts = pd.Series(maps.str[1].value_counts())

valid_maps = map_counts[map_counts > min_map_play_count]
valid_map_names = valid_maps.index

# Grab the first and second word of the mapname
first_map_word_length = maps.str[0].str.split(" ").apply(len)
first_map_word = maps.str[0].str.split(" ").str[0]
second_map_word = maps.str[1]

first_map_length_check = first_map_word_length == 1
first_map_check = first_map_word.isin(valid_map_names)
second_map_check = second_map_word.isin(valid_map_names)

info_correct['map_check'] = (first_map_length_check & first_map_check) | (second_map_check)

correct_map = info_correct[info_correct['map_check'] == True].copy()

players = players[players['id'].isin(correct_map['id'])]

# endregion

## Rename Scout and Soldier to Scout_1 etc ##
# region RENAME COMBAT

# Copy the DataFrame so we don't overwrite the original
players_fixed = players.copy()

# Group by match id and team
grouped = players_fixed.groupby(['id', 'team'])

# Function to randomly rename duplicate classes within each group
def rename_classes_randomly(df):
    random.seed(123)
    np.random.seed(123)
    df = df.copy()  # avoid SettingWithCopyWarning
    for cls in ['scout', 'soldier']:
        indices = df.index[df['primary_class'] == cls].tolist()
        if len(indices) == 2:
            # Randomly shuffle the suffixes
            suffixes = [f"{cls}_1", f"{cls}_2"]
            random.shuffle(suffixes)
            for i, idx in enumerate(indices):
                df.at[idx, 'primary_class'] = suffixes[i]
    return df

# Apply function to each group
players_fixed = grouped.apply(rename_classes_randomly, include_groups=False).reset_index()

# Drop the redundant index column
players_fixed.drop('level_2', axis=1, inplace=True)

# endregion

# Drop Columns That Dont work or are too highly correlated
# region DROP COLS

players_fixed.drop(drop_cols,axis =1,inplace = True)

combat_classes = ['scout', 'soldier', 'demoman']
pattern = '|'.join(combat_classes)  # Creates 'scout|soldier|demoman'
combat_players = players_fixed[players_fixed['primary_class'].str.contains(pattern, case=False, na=False)].copy()

# Make medic stats
medic_players = players_fixed[players_fixed['primary_class'] == 'medic'].copy()

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
       df.fillna(0,inplace=True)

# Remove medicstats. from colnames

medic_players.columns = [col.replace("medicstats.","") for col in medic_players.columns]


# endregion

# WIDEN DATASETS
# region WIDEN DATASETS
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

# endregion

# Merge Medic, Combat,Mapname, and Winner Together
# region MERGE
# Remove duplicate columns
medic_merger = medic_wide.drop(['id','team'],axis =1)

# Merge medic and combat
players_wide = pd.concat([combat_wide,medic_merger],axis = 1)

players_wide = players_wide.merge(teams[['id','team','winner']],on =['id','team'])
# endregion

# Make X and y
# region MAKE X AND Y

drop_cols = ['id','team','winner'] + [col for col in players_wide if 'steamid' in col]

X = players_wide.drop(drop_cols,axis = 1).copy()

y = players_wide['winner']

# endregion

# Rank Normalize all Predictors
# region RANK NORMALIZE

# Rank the scout and soldier data based on the entire dataset, not the pivot version
scout_soldier = X[[col for col in X.columns if 'scout' in col or 'soldier' in col]].copy()

# Turn the data into long
scout_soldier_long = pd.DataFrame()
for index in ['1','2']:
    df = scout_soldier[[col for col in scout_soldier.columns if index in col]].copy()
    df.columns = [col.replace("_"+index,"") for col in df.columns]
    df['num']= index
    scout_soldier_long = pd.concat([scout_soldier_long,df])

# Drop index and rank
num = scout_soldier_long['num']
scout_soldier_long.drop("num",axis =1,inplace = True)
ranked_scout_soldier = scout_soldier_long.rank(pct=True)

# Re attach index
ranked_scout_soldier['num'] = num

# Widen the datset again
scout_soldier = pd.DataFrame()
for index in ['1','2']:
    df = ranked_scout_soldier[ranked_scout_soldier['num'] == index].copy()
    df.drop('num',axis = 1,inplace = True)
    df.columns = [col + "_" + index for col in df.columns]
    scout_soldier = pd.concat([scout_soldier,df],axis = 1)


# Rank the medic and demo stats
medic_demo = X[[col for col in X.columns if 'scout' not in col and 'soldier' not in col]].copy()

medic_demo = medic_demo.rank(pct=True)

# Merge data back together

X = pd.concat([scout_soldier,medic_demo],axis = 1)

# endregion

# Drop 30 Least Useful Predictors
# These are gotten from a previous model iteration 
# region DROP NON USEFUL PREDICTORS

X.drop(unimportant_columns,axis =1, inplace = True)

# endregion

# Merge Map NOT USED BC NOT IMPORTANT
# region MAP MERGE!!!
# Map name
map_list = []

for map in correct_map['map'].str.lower().values:
    for map_name in valid_map_names:
        if map_name in map:
            map_list.append(map_name)

correct_map['map_name'] = map_list

# Bind that sucker in
# team_maps = players_wide.merge(correct_map[['id','map_name']],on = 'id')['map_name']
# map_dummies = pd.get_dummies(team_maps)
# X = pd.concat([X,map_dummies],axis =1 )
# X = X.astype({col: bool for col in X.select_dtypes(include='object').columns})

# endregion

# Output to pkl

model_ready_data_dict = {
     'X':X,
     'y':y
}

joblib.dump(model_ready_data_dict,'../data/pkls/model_ready_data_dict.pkl')

print("Successfully dumped Model Ready Data to pkl")
