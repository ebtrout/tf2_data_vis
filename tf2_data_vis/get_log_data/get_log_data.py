from .request_log_data import * 
from .request_log_info import * 
from .bind_logs import *
from .save_data import * 
from .manipulate_logs import * 
import pandas as pd

pd.set_option('future.no_silent_downcasting', True)
def get_log_data(
                 request_logs = False,
                 request_params = {
                     "n": 250,
                     "cutoff_date": '2016-07-07',
                     "request_start" : 0,
                     "print_interval" : 1,
                     "limit": 1000,
                     "offset_change": 950,
                     "title_includes": "RGL"
                 },
                 update_log_info = True,
                 datasets_as_csv = True,
                 change_output_dir = None,
                 parent_dir = None,
                 ):
    
    # Initialize
    n = request_params['n']
    cutoff_date = request_params['cutoff_date']
    request_start = request_params['request_start']
    print_interval = request_params['print_interval']
    limit = request_params['limit']
    offset_change = request_params['offset_change']
    title = request_params['title_includes']
    
    # If user wants to request logs from API
    # Otherwise read from file
    if request_logs == True:
        print("Requesting logs from logs.tf API")
        log_info_df = request_log_info(limit = limit, 
                        title = title,
                        offset_change = offset_change, 
                        n = n,
                        date = cutoff_date,
                        start = request_start,
                        print_interval = print_interval)
        
        log_data = request_log_data(log_info_df=log_info_df,
                                print_interval=print_interval)
    else:
        print("Reading Log info and Log Data from existing files")
        log_info_df = pd.read_csv('../../data/log_info_df.csv') 

        log_data = joblib.load('../../data/pkls/log_data.pkl')
    
    # If user wants to update the existing data
    
    clean_log_data,error_logs = manipulate_logs(log_data = log_data,
                                                print_interval = print_interval)

    df_dict = bind_logs(clean_log_data=clean_log_data,
                        print_interval= print_interval)
    if update_log_info == True:
        print("Overwriting existing log_info_df.csv and log_data.pkl")
        save_data(log_info_df = log_info_df, 
            log_data = log_data,
        clean_log_data= clean_log_data,
        error_logs= error_logs,
        df_dict= df_dict,
        datasets_as_csv= datasets_as_csv,
        parent_dir = parent_dir)
    elif update_log_info == False: 
        print("Keeping existing log_info_df.csv and log_data.pkl")
        save_data(
        clean_log_data= clean_log_data,
        error_logs= error_logs,
        df_dict= df_dict,
        datasets_as_csv= datasets_as_csv,
        change_output_dir= change_output_dir,
        parent_dir = parent_dir)

