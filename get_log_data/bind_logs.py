import sys
import os
import joblib
import numpy as np
import pandas as pd

pd.set_option('future.no_silent_downcasting', True)

# Grab the class object from the log_manipulation folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log_manipulation')))


from log import log # type: ignore

file_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(file_dir)

rgl_data = joblib.load("../data/pkls/rgl_log_list.pkl")

df_dict = {
        'info':pd.DataFrame(),
        'players': pd.DataFrame(),
        'teams': pd.DataFrame(),
        'rounds':pd.DataFrame(),
        'player_rounds': pd.DataFrame(),
        'class_kda':pd.DataFrame(),
        'push_stats': pd.DataFrame(),
        'team_medic_stats': pd.DataFrame(),
        'healspread': pd.DataFrame(),
        'round_events':pd.DataFrame(),
        'medic_stats':pd.DataFrame(),
    }


for i,log_data in enumerate(rgl_data):
    id = log_data.id
    if i % np.floor(len(rgl_data) / 20) == 0 and i !=0:
        print(f"{i}/{len(rgl_data)}")
    log_df_dict = {
        "info" : log_data.info,
        "players" : log_data.players,
        "teams" : log_data.teams,
        "rounds" : log_data.rounds,
        "player_rounds" : log_data.player_rounds,
        "class_kda" : log_data.class_kda,
        "push_stats" : log_data.push_stats,
        "team_medic_stats" : log_data.team_medic_stats,
        "healspread" : log_data.healspread,
        "round_events": log_data.round_events,
        "medic_stats": log_data.medic_stats
    }
    
    for key in log_df_dict.keys():
        log_df = log_df_dict[key]
        df = df_dict[key]
        log_df['id'] = id    

        df = pd.concat([df,log_df])
        
        # Reorder cols to have id first
        df = df[['id'] + [col for col in df.columns if col !='id']]
        df_dict[key] = df
    
joblib.dump(df_dict,'../data/pkls/rgl_df_dict.pkl')
    
    
    



    
