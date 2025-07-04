import pandas as pd
import requests
from pandas import json_normalize
import numpy as np

def request_log_info(limit = 100, 
                     title = "RGL",offset_change = 80, 
                     n = 2000,date = '2016-07-07',start = 0,
                     print_interval = 50):

    #### Grab RGL Logs from Logs.tf API ####

    # region request function
    def request_rgl_logs(offset = 0,limit = 100,title = "RGL"):
        url = f'http://logs.tf/api/v1/log?title= {title} &limit={limit}&offset={offset}'
        response = requests.get(url)
            
        if response.status_code == 200:
            result = response.json()
        else:
            print("Failed to retrieve data from the URL:", response.status_code)
        
        log_info = json_normalize(result['logs'])
        
        if 'date' in log_info.columns:
            log_info.sort_values(by='date', ascending=True)
            log_info['date'] = pd.to_datetime(log_info['date'], unit='s')
        else: 
            return None
        

        lower_title = title.lower()

        if 'title' in log_info.columns:
            # Only keep logs with RGL in title
            log_info = log_info[(log_info['title'].str.lower().str.contains(lower_title))]
        else: 
            return None

        return(log_info)
    # endregion

    # region use the request function
    log_info_df = pd.DataFrame()
    # Loop for n rounds and request log info and add them to the df
    count = 0 
    for i in range(start,n+1):
        count = count + 1
        if count == print_interval:
            s = f'Requested {i} / {n} rounds of log info'
            count = 0
            print(s)
        
        result = request_rgl_logs(offset = i * offset_change,
                                  limit = limit,title = title)
        if type(result) != type(None):
            log_info_df = pd.concat([log_info_df,result])

    ### SUBSET DOWN TO REMOVE BAD LOGS

    # Incorrect plauer numbers
    log_info_df = log_info_df[log_info_df['players'] > 11]
    log_info_df = log_info_df[log_info_df['players'] < 14]

    # :Limiit to past the specified date
    log_info_df['date'] = pd.to_datetime(log_info_df['date'])
    log_info_df = log_info_df[log_info_df['date'] > date]

    # Drop Dupes
    log_info_df = log_info_df.drop_duplicates()

    # Remove maps that arent cp maps
    log_info_df = log_info_df[~log_info_df['map'].str.startswith("pl_")]
    log_info_df = log_info_df[~log_info_df['map'].str.startswith("pass_")]
    # endregion
    return log_info_df