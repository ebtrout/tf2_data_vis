from get_log_data.get_log_data import *
import os


parent_dir = os.path.dirname(os.path.abspath(__file__))

get_log_data(    request_logs = False,
                 request_params = {
                     "n": 0,
                     "cutoff_date": '2016-07-07',
                     "request_start" : 0,
                     "print_interval" : 1,
                     "limit": 5,
                     "offset_change": 1,
                     "title_includes": "RGL"
                 },
                 update_log_info = False,
                 datasets_as_csv = True,
                 parent_dir = parent_dir,
                 change_output_dir = None,
                 debug = False
            )