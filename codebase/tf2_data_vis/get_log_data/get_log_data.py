from .request_log_data import * 
from .request_log_ids import * 
from .bind_logs import *
from .save_data import * 
from .manipulate_logs import * 
from .filter_log_ids import *
from .batch import *
import pandas as pd
import os

pd.set_option('future.no_silent_downcasting', True)
def get_log_data(
                    batch_size = 100,
                    request_ids = False,
                    request_data = False,
                    update_log_ids = True,
                    filter_logs = True,
                    output_dir = "data",
                    manipulate_log_data = True,
                    parent_dir = None,
                    debug = False,
                    request_params = {
                        "n": 250,
                        "cutoff_date": '2016-07-07',
                        "request_start" : 0,
                        "limit": 1000,
                        "offset_change": 950,
                        "title_includes": "RGL",
                        "sleep_between_requests": 1
                    }
                
                ):
    
    # Initialize
    if request_params['limit'] > 10000:
        request_params['limit'] = 10000
        print('limit too high: setting to 10,000')

    # If user wants to request logs from API
    if request_ids == True:
        print("Requesting logs from logs.tf API")
        request_log_ids(
            request_params= request_params,
            batch_size = batch_size,
            parent_dir = parent_dir,
            output_dir = output_dir
            )
        
    # Join the batches
    print("Joining batches of log ids")
    log_ids = join_batch_df(
        batch_type = "log_id",
        parent_dir = parent_dir,
        output_dir=output_dir,
    )
    
    if filter_logs == True:
        log_ids = filter_log_ids(
            log_ids = log_ids,
            map_cutoff= 100,
            request_params= request_params
            )
        if len(log_ids) == 0:
            raise Exception("No Valid Ids After Filtering")
    
    # If user wants to request logs data from API
    if request_data == True:
        request_log_data(
            log_ids =log_ids,
            request_params = request_params,
            batch_size = batch_size,
            parent_dir = parent_dir,
            output_dir = output_dir
        )

    # Grab log_data from batches 
    print("Joining batches of log data")
    log_data = join_batch_dict(
        batch_type = "log_data",
        parent_dir = parent_dir,
        output_dir=output_dir,
    )

    # If user wants to manipulate the log data and not just grab log ids
    if manipulate_log_data == True:    
        manipulate_logs(
        log_data = log_data,
        batch_size= batch_size,
        output_dir= output_dir,
        parent_dir= parent_dir,
        debug = debug
        )
        print("Joining batches of clean_log data")
        clean_log_data = join_batch_dict(
            batch_type = "clean_log_data",
            parent_dir = parent_dir,
            output_dir=output_dir,
        )

        print("Joining batches of clean_log data")
        error_logs = join_batch_dict(
            batch_type = "error_logs",
            parent_dir = parent_dir,
            output_dir=output_dir,
        )


        # Bind them all together in batches
        bind_logs(
            clean_log_data=clean_log_data,
            batch_size= batch_size,
            output_dir= output_dir,
            parent_dir= parent_dir,
            )
        print("Joining batches of df_dict's of individual csvs")

        df_dict = join_batch_df_dict(
            output_dir= output_dir,
            parent_dir= parent_dir,
        )
        

        # If user wants to replace existing log_ids and log_data
        if update_log_ids == True:
            print("Overwriting existing log_ids.csv and log_data.pkl")
            save_data(
            log_ids = log_ids, 
            log_data = log_data,
            clean_log_data= clean_log_data,
            error_logs= error_logs,
            output_dir = output_dir,
            df_dict= df_dict,
            parent_dir = parent_dir
            )
            
        elif update_log_ids == False: 
            print("Keeping existing log_ids.csv and log_data.pkl")
            save_data(
            clean_log_data= clean_log_data,
            error_logs= error_logs,
            df_dict= df_dict,
            output_dir= output_dir,
            parent_dir = parent_dir
            )