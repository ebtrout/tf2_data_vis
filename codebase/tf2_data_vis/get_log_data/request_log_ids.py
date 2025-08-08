import pandas as pd
import requests
from pandas import json_normalize
from .save_batch import save_batch
import numpy as np
import time

def request_log_ids(request_params: dict,
                    batch_size = 100,
                    output_dir = None,
                    parent_dir = None):

    #### Grab RGL Logs from Logs.tf API ####

    n = request_params['n']
    request_start = request_params['request_start']
    limit = request_params['limit']
    offset_change = request_params['offset_change']
    title_includes = request_params['title_includes']    

    # region use the request function
    log_id_df = pd.DataFrame()
    # Loop for n rounds and request log info and add them to the df
    batch_counter = 1
    for i in range(0,n):
        print(f'Requested {i} / {n} rounds of log info')
        
        
        # Try to request the logs if error occurs, return None
        try:
            result = request_log_id(offset = request_start + (i * offset_change),
                                    limit = limit,
                                    title = title_includes,
                                    request_params = request_params)
        except Exception as e:
            print(f"Encountered an Issue:{e}")
            result = None
        
        # Apply some basic checks
        filtered_result = filter_result(result = result,request_params = request_params)

        # Append it if the result was successful
        if type(filtered_result) != type(None):
            log_id_df = pd.concat([log_id_df,filtered_result])
        
        if i % batch_size == 0 or i == n - 1:
            save_batch(batch = batch_counter,
                       batch_type = "log_id",
                       parent_dir = parent_dir,
                       output_dir=output_dir,
                       object = log_id_df
                       )
            batch_counter += 1
            log_id_df = pd.DataFrame()
            
    return log_id_df


# region request function
def request_log_id(offset = 0,limit = 100,title = "",request_params = {}):
    sleep_between_requests = request_params['sleep_between_requests']
    time.sleep(sleep_between_requests)
    if title != "":
        url = f'http://logs.tf/api/v1/log?title={title}&limit={limit}&offset={offset}'
    else:
        url = f'http://logs.tf/api/v1/log?&limit={limit}&offset={offset}'
    response = requests.get(url)
        
    if response.status_code == 200:
        result = response.json()
    else:
        result = np.nan
        print("Failed to retrieve data from the URL:", response.status_code)
        return None

    log_id = json_normalize(result['logs'])

    return(log_id)
# endregion

def filter_result(result,request_params = {}):
    title_includes = request_params['title_includes']    
    
    if 'date' in result.columns:
        result.sort_values(by='date', ascending=True)
        result['date'] = pd.to_datetime(result['date'], unit='s')
    else: 
        return None
    
    if 'title' in result.columns:
        # Only keep logs with RGL in title
        result = result[(result['title'].str.lower().str.contains(title_includes.lower()))]
    else: 
        return None
    
    return result