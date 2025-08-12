import os
import pandas as pd
import joblib
import numpy as np
def clean_map_name(parent_dir,output_dir):
    # Find valid map names
    path = os.path.join(parent_dir,'..',output_dir,'info.csv')
    info = pd.read_csv(path)

    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    model_ready_data_dict = joblib.load(path)

    path = os.path.join(parent_dir,'..',output_dir,'valid_ids.csv')
    valid_ids = pd.read_csv(path)

    info_correct = info[info['id'].isin(model_ready_data_dict['ids'])].copy()
    maps = info_correct['map'].str.lower().str.split("_")
    map_counts = pd.Series(maps.str[1].value_counts())


    valid_maps = map_counts[map_counts > 50]
    valid_map_names = valid_maps.index
    valid_info = info[info['id'].isin(valid_ids['id'])].copy()

    map_names = list(valid_info['map'].str.lower().str.split("_").str[1].value_counts().index)

    map_counts = []
    for map in info['map'].str.lower().values:
        i = 0
        for map_name in map_names:
            if i > 0:
                continue
            if  type(map) == type(np.nan):
                map_counts.append(np.nan)
                i +=1
            elif map_name in map:
                map_counts.append(map_name)
                i += 1
            

    # Define a function to find the first match
    def find_match(text):
        if type(text) == type(np.nan):
            return np.nan
        for keyword in map_names:
            if keyword in text.lower():
                return keyword
        return np.nan  # if no match found

    # Apply the function row by row
    info['clean_map_name'] = info['map'].apply(find_match)
    path = os.path.join(parent_dir,'..',output_dir,'info.csv')
    info.to_csv(path,index = False)
