from .request_log_data import * 
from .request_log_ids import * 
from .bind_logs import *
from .save_data import * 
from .manipulate_logs import * 
import pandas as pd
import os

pd.set_option('future.no_silent_downcasting', True)
def get_log_data(
                batch_size = 100,
                request_logs = False,
                request_params = {
                    "n": 250,
                    "cutoff_date": '2016-07-07',
                    "request_start" : 0,
                    "limit": 1000,
                    "offset_change": 950,
                    "title_includes": "RGL",
                    "sleep_between_requests": 1
                },
                update_log_ids = True,
                datasets_as_csv = True,
                output_dir = "data",
                manipulate_log_data = True,
                parent_dir = None,
                debug = False,
                request_only_ids = False
                 ):
    
    # Initialize
    if request_params['limit'] > 10000:
        request_params['limit'] = 10000
        print('limit too high: setting to 10,000')

    # If user wants to request logs from API
    # Otherwise read from file
    if request_logs == True:
        print("Requesting logs from logs.tf API")
        log_ids = request_log_ids(
            request_params= request_params,
            batch_size = batch_size,
            parent_dir = parent_dir,
            output_dir =output_dir
            )
        
        if request_only_ids == False:
            log_data = request_log_data(
                log_ids =log_ids,
                request_params = request_params
                )
    else:
        print("Reading Log info and Log Data from existing files")
        log_ids = pd.read_csv('../../data/log_ids.csv') 

        log_data = joblib.load('../../data/pkls/log_data.pkl')
    
    # If user wants to manipulate the log data and not just grab log ids
    if manipulate_log_data == True and request_only_ids == False:    
        clean_log_data,error_logs = manipulate_logs(
            log_data = log_data,
            debug = debug
            )

        # Bind them all together
        df_dict = bind_logs(
            clean_log_data=clean_log_data,
            )
        
        # If user wants to replace existing log_ids and log_data
        if update_log_ids == True:
            print("Overwriting existing log_ids.csv and log_data.pkl")
            print(output_dir)
            save_data(
            log_ids = log_ids, 
            log_data = log_data,
            clean_log_data= clean_log_data,
            error_logs= error_logs,
            output_dir = output_dir,
            df_dict= df_dict,
            datasets_as_csv= datasets_as_csv,
            parent_dir = parent_dir
            )
            
        elif update_log_ids == False: 
            print("Keeping existing log_ids.csv and log_data.pkl")
            print(output_dir)
            save_data(
            clean_log_data= clean_log_data,
            error_logs= error_logs,
            df_dict= df_dict,
            datasets_as_csv= datasets_as_csv,
            output_dir= output_dir,
            parent_dir = parent_dir
            )
    elif manipulate_log_data == False and request_only_ids == True:
        save_data(
            parent_dir = parent_dir,
            output_dir = output_dir,
            log_ids = log_ids
        )
    elif manipulate_log_data == True and request_only_ids == False:
        print("invalid combination of manipulate_log_data and request_only_ids")
