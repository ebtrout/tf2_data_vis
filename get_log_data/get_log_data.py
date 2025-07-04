from request_log_info import request_log_info
from request_log_data import request_log_data
from manipulate_logs import manipulate_logs
from bind_logs import bind_logs
from save_data import save_data
import pandas as pd
import joblib
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

id_compare = pd.read_csv("../data/log_info_df_old.csv")


log_info_df = request_log_info(limit = 100, 
                     title = "RGL",offset_change = 80, 
                     n = 3000,date = '2016-07-07',start = 0,
                     print_interval = 10)

log_info_df = log_info_df[~log_info_df['id'].isin(id_compare['id'])]

log_data = request_log_data(log_info_df=log_info_df,
                            print_interval=1)
clean_log_data,error_logs = manipulate_logs(log_data = log_data,print_interval = 1)

df_dict = bind_logs(clean_log_data=clean_log_data,print_interval= 1)

save_data(log_info_df = log_info_df, log_data = log_data,
          clean_log_data= clean_log_data, error_logs= error_logs,
          df_dict= df_dict, datasets_as_csv= True)
