import joblib
import os



def save_data(log_ids = None,
              log_data = None,
              clean_log_data = None,
              error_logs = None,
              df_dict = None,
              datasets_as_csv = True,
              output_dir = None,
              parent_dir = None):
    if type(output_dir) == type(None) or output_dir == "":
        output_dir = "data"
    
    # Make paths
    path = f'../{output_dir}'
    folder_path = os.path.join(parent_dir, path)

    os.makedirs(folder_path, exist_ok=True) 
    
    path = f'../{output_dir}/pkls'
    folder_path = os.path.join(parent_dir, path)

    os.makedirs(folder_path, exist_ok=True) 
    
    
    if type(log_ids) != type(None):     
        path = f'../{output_dir}/log_ids.csv'
        file_path = os.path.join(parent_dir, path)
        log_ids.to_csv(file_path)
        print("Saved log_ids.csv to data folder")

    if type(log_data) != type(None):     
        # log_data to pkl
        path = f'../{output_dir}/pkls/log_data.pkl'
        file_path = os.path.join(parent_dir, path)
        joblib.dump(log_data, file_path)
        print("Dumped log_data to pkl file")
    
    if type(clean_log_data) != type(None):     
        # clean_log_data
        path = f'../{output_dir}/pkls/clean_log_data.pkl'
        file_path = os.path.join(parent_dir, path)
        joblib.dump(clean_log_data, file_path)
        print("Dumped clean_log_data to pkl file")

    if type(error_logs) != type(None):     
        # Error_logs
        path = f'../{output_dir}/pkls/error_logs.pkl'
        file_path = os.path.join(parent_dir, path)
        joblib.dump(error_logs,file_path)
        print("Dumped error_logs to pkl file")

    if type(df_dict) != type(None):     
        # df_dict
        path = f'../{output_dir}/pkls/df_dict.pkl'
        file_path = os.path.join(parent_dir, path)

        joblib.dump(df_dict, file_path)
        print("Dumped df_dict to pkl file")

    # Save into csv
    if datasets_as_csv == True and type(df_dict) != type(None):
        print("Saving")
        print(df_dict.keys())
        print("To csvs")
        for key in df_dict.keys():
            df = df_dict[key]
            path = f'../{output_dir}/{key}.csv'
            file_path = os.path.join(parent_dir, path)
            df.to_csv(file_path)