import pandas as pd
import os

def long_players(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'players.csv')
    players = pd.read_csv(path)
    normal_cols = ['kills','deaths','assists','dmg','dmg_real','dt','dt_real','hr']
    pct_cols = ['kill_pct','deaths_pct','assists_pct','dmg_pct','dmg_real_pct','dt_pct','dt_real_pct','hr_pct']

    both_cols = ['id','team','steamid','name','primary_class']

    normal_df = players[both_cols + normal_cols].copy()
    pct_df = players[both_cols + pct_cols].copy()

    pct_df.columns = normal_df.columns

    normal_df['coltype'] = "Raw"
    pct_df['coltype'] = "Pct of Team"


    long_player = pd.concat([normal_df,pct_df])

    long_player = long_player.fillna(0)
    
    path = os.path.join(parent_dir,'..',output_dir,'long_players.csv')

    long_player.to_csv(path,index = False)

def class_kda_long(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'players.csv')
    players = pd.read_csv(path)

    class_cols = [col for col in players.columns if "class_kda" in col]

    class_kill = [col for col in class_cols if "kills" in col and "kdapd" not in col]

    class_deaths= [col for col in class_cols if "deaths" in col and "kdapd" not in col]

    class_assists = [col for col in class_cols if "assists" in col and "kdapd" not in col]

    class_kill_pd = [col for col in class_cols if "kills" in col and "kdapd" in col]

    class_deaths_pd = [col for col in class_cols if "deaths" in col and "kdapd" in col]

    class_assists_pd = [col for col in class_cols if "assists" in col and "kdapd" in col]

    keep_cols = ['id','team','steamid','name','primary_class']



    class_dict = {
        "Kills" : class_kill,
        "Deaths" : class_deaths,
        "Assists" : class_assists,
        "K/D" : class_kill_pd,
        "A/D" : class_assists_pd,
        "Death Rate" : class_deaths_pd
    }

    long_class = pd.DataFrame()
    for key in class_dict.keys():
        col_type = key
        l = class_dict[key]
        df = players[keep_cols + l].copy()
        df.columns = keep_cols + [col.split("_")[0] for col in df.columns if col not in keep_cols] 
        df['col_type'] = col_type
        long_class = pd.concat([long_class,df])

    long_class = long_class.fillna(0)
    path = os.path.join(parent_dir,'..',output_dir,'class_kda_long.csv')
    long_class.to_csv(path,index = False)