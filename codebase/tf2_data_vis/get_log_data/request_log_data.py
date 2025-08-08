import joblib
import requests
import numpy as np
from .batch import save_batch
import time
import pandas as pd

## Go through all RGL logs saved from log_info.py and grab the data for each of them ##
# Each id is passed to the logs.tf API and returned a JSON file #

def request_log_data(log_ids:pd.DataFrame,
                     request_params:dict,
                     batch_size = 100,
                     output_dir = None,
                     parent_dir = None):
    sleep_between_requests = request_params['sleep_between_requests']

    # Loop and save jsons to a list 
    log_data = {}

    batch_counter = 1
    for i,id in enumerate(log_ids['id'].values):
        print(f'Requested {i+1} / {len(log_ids)} Individual log data')
        try:
            time.sleep(sleep_between_requests)
            url = f'https://logs.tf/api/v1/log/{id}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
            else:
                print("Failed to retrieve data from log:{log}:", response.status_code)
            
            log_data[id] = data
        except Exception as e:
            print(f'log:{id} encountered {e} while requesting log data')
        if i % batch_size == 0 or i == len(log_ids) or i == len(log_ids) -1 or i == len(log_ids) + 1:
            save_batch(batch = batch_counter,
                       batch_type = "log_data",
                       parent_dir = parent_dir,
                       output_dir=output_dir,
                       object = log_data
                       )
            batch_counter += 1
            log_data = {}

    return