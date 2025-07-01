import sys
import os
import joblib
import numpy as np
import pandas as pd

# Set option to stop thousands of warnings 
pd.set_option('future.no_silent_downcasting', True)

# Grab the class object from the log_manipulation folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'log_manipulation')))


from log import log # type: ignore

# Import RGL Logs

rgl_logs = joblib.load('data/pkls/rgl_logs_pre_manip.pkl')
rgl_log_info = joblib.load('data/pkls/rgl_log_info.pkl')

rgl_data = []
error_logs = []

ids = rgl_log_info['id'].values

for i in range(0,len(rgl_logs)):
    rgl_match = rgl_logs[i]
    id = ids[i]

    # Print The Progress
    if i % np.floor(len(rgl_logs) / 10) == 0 and i != 0:
        print(f'{i} / {len(rgl_logs)}')

    # Try to turn log data into clean log class object
    # If successful, add to rgl_data list
    try:
        make_log = log(log = rgl_match,id = id)
        rgl_data.append(make_log)
    # Errors are added to the error_data list
    except Exception as e:
        print(f"Skipping index {i} due to error: {e}")
        error_logs.append(rgl_match)
        continue        

joblib.dump(rgl_data,'data/pkls/rgl_log_list.pkl')

