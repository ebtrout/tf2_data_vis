import pandas as pd
import joblib
import os

def save_batch(batch: int = None,
               parent_dir = None,
               output_dir = None,
               batch_type: str = None,
               object= None):
    output_path = os.path.join(parent_dir,'..',output_dir)
    pkl_path = os.path.join(output_path,'pkls')
    folder_path = os.path.join(pkl_path,batch_type)

    file_suffix = f'_batch_{batch}.pkl'
    filename = batch_type + file_suffix
    file_path = os.path.join(folder_path,filename)

    os.makedirs(folder_path, exist_ok=True)

    joblib.dump(object,file_path)
    print(f'Dumped {batch_type}_batch_{batch} to pkl')

def join_batch_df(
               parent_dir = None,
               output_dir = None,
               batch_type: str = None,
    ):
    output_path = os.path.join(parent_dir,'..',output_dir)
    pkl_path = os.path.join(output_path,'pkls')
    folder_path = os.path.join(pkl_path,batch_type)
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    batches = []
    for f in files:
        file_path = os.path.join(folder_path,f)
        print(file_path)
        batch = joblib.load(file_path)
        batches.append(batch)
    return pd.concat(batches)

def join_batch_dict(
               parent_dir = None,
               output_dir = None,
               batch_type: str = None,
    ):
    output_path = os.path.join(parent_dir,'..',output_dir)
    pkl_path = os.path.join(output_path,'pkls')
    folder_path = os.path.join(pkl_path,batch_type)
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    batches = {}
    for f in files:
        file_path = os.path.join(folder_path,f)
        batch = joblib.load(file_path)
        for key in batch.keys():
            batches[key] = batch[key]
    return batches

def join_batch_df_dict(
               parent_dir = None,
               output_dir = None,
    ):
    output_path = os.path.join(parent_dir,'..',output_dir)
    pkl_path = os.path.join(output_path,'pkls')
    folder_path = os.path.join(pkl_path,"df_dict")
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    master_dict = {
        'info': [],
        'players': [],
        'teams': [],
        'rounds': [],
        'player_rounds': [],
        'class_kda': [],
        'push_stats': [],
        'team_medic_stats': [],
        'healspread': [],
        'healspread_grouped': [],
        'round_events': [],
        'medic_stats': [],
    }
    for f in files:
        file_path = os.path.join(folder_path,f)
        batch = joblib.load(file_path)
        for key,df in batch.items():
            master_dict[key].append(df)

    for key in master_dict:
        master_dict[key] = pd.concat(master_dict[key], ignore_index=True)
    
    return master_dict
        
    
    

