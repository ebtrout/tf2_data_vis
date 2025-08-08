import pandas as pd
import joblib
import os

def save_batch(batch: int = None,
               parent_dir = None,
               output_dir = None,
               batch_type: str = None,
               object= None):
    output_path = os.path.join(parent_dir,output_dir)
    folder_path = os.path.join(output_path,batch_type)

    file_suffix = f'_{batch}.pkl'
    filename = batch_type + file_suffix
    file_path = os.path.join(folder_path,filename)

    os.makedirs(folder_path, exist_ok=True)

    joblib.dump(object,file_path)