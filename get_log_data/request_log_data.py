import joblib
import pandas as pd
import requests
from pandas import json_normalize
import numpy as np
import os
import time

## Go through all RGL logs saved from log_info.py and grab the data for each of them ##
# Each id is passed to the logs.tf API and returned a JSON file #
# Added to a list and then saved to a pkl #


file_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(file_dir)


rgl_logs = joblib.load("../data/rgl_log_info.pkl")


# Loop and save jsons to a list 
saved_logs = []
for i,match in enumerate(rgl_logs['id'].values):
    # Sleep for 1 second to avoid overloading the api
    time.sleep(1)
    log = match
    url = f'https://logs.tf/api/v1/log/{log}'
    response = requests.get(url)

    
    if response.status_code == 200:
        data = response.json()
        if i % np.floor(len(rgl_logs) / 150) == 0:
            print(f'{i} / {len(rgl_logs)}')
    else:
        print("Failed to retrieve data from log:{log}:", response.status_code)
    
    saved_logs.append(data)

joblib.dump(saved_logs,'../data/pkls/rgl_logs_pre_manip.pkl')