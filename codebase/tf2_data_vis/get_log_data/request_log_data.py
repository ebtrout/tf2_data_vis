import joblib
import requests
import numpy as np
import time
import pandas as pd

## Go through all RGL logs saved from log_info.py and grab the data for each of them ##
# Each id is passed to the logs.tf API and returned a JSON file #

def request_log_data(log_ids:pd.DataFrame,request_params:dict):
    print_interval = request_params['print_interval']
    sleep_between_requests = request_params['sleep_between_requests']

    # Loop and save jsons to a list 
    log_data = {}

    for i,id in enumerate(log_ids['id'].values):
        try:
            time.sleep(sleep_between_requests)
            url = f'https://logs.tf/api/v1/log/{id}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if count == print_interval:
                    count = 0
                    print(f'Requested {i} / {len(log_ids)} Individual log data')
            else:
                print("Failed to retrieve data from log:{log}:", response.status_code)
            
            log_data[id] = data
        except Exception as e:
            print(f'log:{id} encountered {e} while requesting log data')

    return log_data