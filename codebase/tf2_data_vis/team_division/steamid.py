import os 
import pandas as pd
import re

def steamid_list(parent_dir,output_dir):
    steamid_df = load_players(parent_dir,output_dir)
    steamid_df['num_games'] = steamid_df.groupby('steamid').transform('size')
    steamid_df.sort_values(by = 'num_games',ascending = False,inplace = True)
    steamid_df = add_steamid64(steamid_df)
    steamid64 = steamid_df['steamid64'].unique()
    return steamid64
    
    

def load_players(parent_dir,output_dir):
    folder = os.path.join(parent_dir,'..',output_dir)
    path = os.path.join(folder,'players.csv')

    players = pd.read_csv(path)
    return(players)

def add_steamid64(players):
    steamid_df = players.copy()
    steamid_df['account_id'] = (
        steamid_df['steamid'].str
        .replace(r'[\[\]]',"",regex = True).str
        .split(":")
        .str[2]
    )
    valve_offset = 76561197960265728
    steamid_df['steamid64'] = steamid_df['account_id'].astype(int) + valve_offset 
    return(steamid_df)

def convert_steamid(s):
    # Remove square brackets
    s = re.sub(r'[\[\]]', '', s)
    
    # Split and take the 3rd part
    s = s.split(":")[2]
    
    # Convert to int and add offset
    valve_offset = 76561197960265728
    s = int(s) + valve_offset
    
    return s  # return as string
