from tf2_data_vis.get_log_data.get_log_data import *
import os


parent_dir = os.path.dirname(os.path.abspath(__file__))

get_log_data(   batch_size = 1,
                request_logs = True,
                request_params = {
                    "n": 4,
                    "cutoff_date": '2016-07-07',
                    "request_start" : 0,
                    "print_interval" : 1,
                    "limit": 10,
                    "offset_change": 1000,
                    "title_includes": "",
                    "sleep_between_requests": 2
                },
                update_log_ids = True,
                datasets_as_csv = False,
                parent_dir = parent_dir,
                output_dir = "testing",
                manipulate_log_data = False,
                debug = False,
                request_only_ids= True,
            )