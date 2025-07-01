import joblib
import pandas as pd
import requests
from pandas import json_normalize
import numpy as np
import os

file_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(file_dir)

#### Grab RGL Logs from Logs.tf API ####
# Save them to a pkl file 

def request_rgl_logs(offset = 0,limit = 100):
    url = f'http://logs.tf/api/v1/log?title= RGL &limit={limit}&offset={offset}'
    response = requests.get(url)
        
    if response.status_code == 200:
        logs = response.json()
    else:
        print("Failed to retrieve data from the URL:", response.status_code)
    
    logs = json_normalize(logs['logs'])
    
    if 'date' in logs.columns:
        logs.sort_values(by='date', ascending=True)
        logs['date'] = pd.to_datetime(logs['date'], unit='s')


    logs = logs[(logs['title'].str.lower().str.contains('rgl')) & (logs['views'])]
    logs = logs[~(logs['title'].str.lower().str.contains(' rgl vs '))]
    logs = logs[~(logs['title'].str.lower().str.contains('vs rgl'))]
    return(logs)

### Parameters to use function
offset_change = 80
n = 2000
limit = 100

start = 0

rgl_logs = pd.DataFrame()
for i in range(start,n+1):
    if i % np.floor((n- start) /50) == 0:
        print(i)
    result = request_rgl_logs(offset = i * offset_change)
    rgl_logs = pd.concat([rgl_logs,result])

### SUBSET DOWN TO REMOVE BAD LOGS

# Incorrect plauer numbers
rgl_logs = rgl_logs[rgl_logs['players'] > 11]
rgl_logs = rgl_logs[rgl_logs['players'] < 14]

# :Limiit to past the Meet Your Match Update
rgl_logs['date'] = pd.to_datetime(rgl_logs['date'])
rgl_logs = rgl_logs[rgl_logs['date'] > '2016-07-07']

# Drop Dupes
rgl_logs = rgl_logs.drop_duplicates()

# Remove maps that arent cp maps
rgl_logs = rgl_logs[~rgl_logs['map'].str.startswith("pl_")]
rgl_logs = rgl_logs[~rgl_logs['map'].str.startswith("pass_")]

joblib.dump(rgl_logs,'../data/pkls/rgl_log_info.pkl')
