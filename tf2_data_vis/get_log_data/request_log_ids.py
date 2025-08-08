import pandas as pd
import requests
from pandas import json_normalize
import numpy as np
import time

def request_log_ids(request_params: dict):

    #### Grab RGL Logs from Logs.tf API ####

    n = request_params['n']
    cutoff_date = request_params['cutoff_date']
    request_start = request_params['request_start']
    print_interval = request_params['print_interval']
    limit = request_params['limit']
    offset_change = request_params['offset_change']
    title_includes = request_params['title_includes']    

    # region use the request function
    log_info_df = pd.DataFrame()
    # Loop for n rounds and request log info and add them to the df
    count = 0 
    for i in range(0,n):
        count = count + 1
        if count == print_interval:
            print(f'Requested {i} / {n} rounds of log info')
            count = 0
        try:
            result = request_rgl_logs(offset = request_start + (i * offset_change),
                                    limit = limit,
                                    title = title_includes,
                                    request_params = request_params)
        except Exception as e:
            print(f"Encountered an Issue:{e}")
            
            result = None
        if type(result) != type(None):
            log_info_df = pd.concat([log_info_df,result])

    ### SUBSET DOWN TO REMOVE BAD LOGS

    # Incorrect plauer numbers
    log_info_df = log_info_df[log_info_df['players'] > 11]
    log_info_df = log_info_df[log_info_df['players'] < 14]

    # :Limiit to past the specified date
    log_info_df['date'] = pd.to_datetime(log_info_df['date'])
    log_info_df = log_info_df[log_info_df['date'] > cutoff_date]

    # Drop Dupes
    log_info_df = log_info_df.drop_duplicates()

    # Remove maps that arent cp maps
    log_info_df = log_info_df[~log_info_df['map'].str.startswith("pl_")]
    log_info_df = log_info_df[~log_info_df['map'].str.startswith("pass_")]
    # endregion
    return log_info_df


# region request function
def request_rgl_logs(offset = 0,limit = 100,title = "",request_params = {}):
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

    log_info = json_normalize(result['logs'])
    
    if 'date' in log_info.columns:
        log_info.sort_values(by='date', ascending=True)
        log_info['date'] = pd.to_datetime(log_info['date'], unit='s')
    else: 
        return None
    
    if 'title' in log_info.columns:
        # Only keep logs with RGL in title
        log_info = log_info[(log_info['title'].str.lower().str.contains(title.lower()))]
    else: 
        return None

    return(log_info)
# endregion