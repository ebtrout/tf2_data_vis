import pandas as pd
from tf2_data_vis.log_manipulation.log import log
from .batch import save_batch

def bind_logs(clean_log_data,
              batch_size = 100,
              output_dir = None,
              parent_dir = None):
    pd.set_option('future.no_silent_downcasting', True)

    # Setup a dict of all dfs needed
    df_dict = initialize_df_dict()
    batch_counter = 1
    # Loop through and append each log's data to the df dict 
    for i,id in enumerate(clean_log_data.keys()):
        log_data =clean_log_data[id]
        id = log_data.id
        # Print Progress
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
            "healspread_grouped" : log_data.healspread_grouped,
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
        if i % batch_size == 0 or i == len(clean_log_data.keys()) or i == len(clean_log_data.keys()) -1 or i == len(clean_log_data.keys()) + 1:
            print(f"Bound {i + 1}/{len(clean_log_data)} logs together")
            save_batch(batch = batch_counter,
                       batch_type = "df_dict",
                       parent_dir = parent_dir,
                       output_dir=output_dir,
                       object = df_dict
                       )
            batch_counter += 1
            df_dict = initialize_df_dict()
    return    
    
    
def initialize_df_dict():
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
            'healspread_grouped': pd.DataFrame(),
            'round_events':pd.DataFrame(),
            'medic_stats':pd.DataFrame(),
        }
    return df_dict


    
