import joblib
import os



def save_data(log_info_df = None,
              log_data = None,
              clean_log_data = None,
              error_logs = None,
              df_dict = None,
              datasets_as_csv = True,
              change_output_dir = None,
              parent_dir = None):
    
    if type(change_output_dir) == type(None):
        change_output_dir = "data"
    
    # Make paths
    path = f'../{change_output_dir}'
    folder_path = os.path.join(parent_dir, path)

    os.makedirs(folder_path, exist_ok=True) 
    
    path = f'../{change_output_dir}/pkls'
    folder_path = os.path.join(parent_dir, path)

    os.makedirs(folder_path, exist_ok=True) 
    
    if type(change_output_dir) == type(None):
        change_output_dir = "data"
    
    
    if type(log_info_df) != type(None):     
        path = f'../{change_output_dir}/log_info_df.csv'
        file_path = os.path.join(parent_dir, path)
        log_info_df.to_csv(file_path)
        print("Saved log_info_df.csv to data folder")

    if type(log_data) != type(None):     
        # log_data to pkl
        path = f'../{change_output_dir}/pkls/log_data.pkl'
        file_path = os.path.join(parent_dir, path)
        joblib.dump(log_data, file_path)
        print("Dumped log_data to pkl file")
    
    if type(clean_log_data) != type(None):     
        # clean_log_data
        path = f'../{change_output_dir}/pkls/clean_log_data.pkl'
        file_path = os.path.join(parent_dir, path)
        joblib.dump(clean_log_data, file_path)
        print("Dumped clean_log_data to pkl file")

    if type(error_logs) != type(None):     
        # Error_logs
        path = f'../{change_output_dir}/pkls/error_logs.pkl'
        file_path = os.path.join(parent_dir, path)
        joblib.dump(error_logs,file_path)
        print("Dumped error_logs to pkl file")

    if type(df_dict) != type(None):     
        # df_dict
        path = f'../{change_output_dir}/pkls/df_dict.pkl'
        file_path = os.path.join(parent_dir, path)

        joblib.dump(df_dict, file_path)
        print("Dumped df_dict to pkl file")

    # Save into csv
    if datasets_as_csv == True:
        print("Saving")
        print(df_dict.keys())
        print("To csvs")
        for key in df_dict.keys():
            df = df_dict[key]
            path = f'../{change_output_dir}/{key}.csv'
            file_path = os.path.join(parent_dir, path)
            df.to_csv(file_path)