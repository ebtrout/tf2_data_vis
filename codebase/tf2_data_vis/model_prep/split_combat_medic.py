import pandas as pd

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
        'hroi', 'dmg_real_pct', 'dmg_pct', 'suicide_rate'
    ]
    return drop_cols
