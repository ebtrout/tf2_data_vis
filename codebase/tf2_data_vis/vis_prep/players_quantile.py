import os
import pandas as pd

def players_quantile(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'players.csv')
    players = pd.read_csv(path)

    path = os.path.join(parent_dir,'..',output_dir,'valid_ids.csv')
    valid_ids = pd.read_csv(path)
    
        # List out columns
    quant_cols = [
        "kills",
        "assists",
        "dmg",
    'dapm',
    'kpd',
    'offclass_pct',
    'kill_pct',
    'deaths_pct',
    'dmg_pct',
    'dmg_real_pct',
    'cpc_pct',
    'ka_pct',
    'assists_pct',
    'dt_pct',
    'dt_real_pct',
    'hroi',
    'assistspd',
    'demoman_kills_class_kdapd',
    'scout_kills_class_kdapd',
    'soldier_kills_class_kdapd',
    'medic_kills_class_kdapd',
        'demoman_deaths_class_kdapd',
    'scout_deaths_class_kdapd',
    'soldier_deaths_class_kdapd',
        'medic_deaths_class_kdapd',
    'dtpm',
    'dt_realpm',
    'healpm',
    'medkits_hppm', 
    'hrpm', 
    'deathspm'

    ]

    # Only grab valid ids to make quanitles on
    sub_players = players[players['id'].isin(valid_ids['id'])].copy()
    sub_players = sub_players[['id',"primary_class",'steamid']+ quant_cols]

    # loop through classes and construct the quantile sets
    ranked_df = pd.DataFrame()
    for class_name in sub_players['primary_class'].unique():
        sub_class = sub_players[sub_players['primary_class'] == class_name].copy()
        
        binding_df = sub_class[['id',"primary_class",'steamid']].copy()
        sub_class.drop(['id',"primary_class",'steamid'],axis = 1,inplace= True)
        
        sub_class = sub_class.rank(pct = True)
        sub_class = pd.concat([binding_df,sub_class],axis = 1)
        
        ranked_df = pd.concat([ranked_df,sub_class])
        
    # Rename columns
    ranked_df.columns = ['id','primary_class','steamid'] + [col + '_quantile' for 
                                                            col in ranked_df.columns if
                                                            col not in ['id','steamid','primary_class']]
    path = os.path.join(parent_dir,'..',output_dir,'players_quantile.csv')
    ranked_df.to_csv(path,index = False)
