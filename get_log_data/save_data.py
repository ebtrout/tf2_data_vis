import joblib
import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def save_data(log_info_df,log_data,clean_log_data,error_logs,df_dict,
              datasets_as_csv = True):
    
    path = '../data/log_info_df.csv'
    log_info_df.to_csv(path)
    print("Saved log_info_df.csv to data folder")

    # log_data to pkl
    path = '../data/pkls/log_data.pkl'
    joblib.dump(log_data,path)
    print("Dumped log_data to pkl file")

    # clean_log_data
    path = '../data/pkls/clean_log_data.pkl'
    joblib.dump(clean_log_data,path)
    print("Dumped clean_log_data to pkl file")

    # Error_logs
    path = '../data/pkls/clean_log_data.pkl'
    joblib.dump(error_logs,path)
    print("Dumped clean_log_data to pkl file")

    # df_dict
    path = '../data/pkls/df_dict.pkl'
    joblib.dump(df_dict,path)
    print("Dumped df_dict to pkl file")

    # Save into csv
    if datasets_as_csv == True:
        for key in df_dict.keys():
            df = df_dict[key]
            path = f'../data/{key}.csv'
            df.to_csv(path)