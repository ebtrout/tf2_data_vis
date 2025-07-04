import joblib
import requests
import numpy as np
import time

## Go through all RGL logs saved from log_info.py and grab the data for each of them ##
# Each id is passed to the logs.tf API and returned a JSON file #

def request_log_data(log_info_df,print_interval = 50):

    # Loop and save jsons to a list 
    log_data = {}
    count = 0

    for i,match in enumerate(log_info_df['id'].values):
        count += 1
        # Sleep for .4 second to avoid overloading the api
        time.sleep(.4)
        log = match
        url = f'https://logs.tf/api/v1/log/{log}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if count == print_interval:
                count = 0
                print(f'Requested {i} / {len(log_info_df)} Individual log data')
        else:
            print("Failed to retrieve data from log:{log}:", response.status_code)
        
        log_data[match] = data

    return log_data