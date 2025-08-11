from tf2_data_vis.get_log_data.get_log_data import *
from tf2_data_vis.model_prep.model_prep import model_prep
import os


parent_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = 'data'
# get_log_data(
#                     batch_size = 100,
#                     request_ids = False,
#                     request_data = False,
#                     filter_logs = True,
#                     update_log_ids = True,
#                     output_dir = "new_data",
#                     manipulate_log_data = True,
#                     parent_dir = parent_dir,
#                     debug = False,
#                     request_params = {
#                         "n": 1,
#                         "cutoff_date": '2016-07-07',
#                         "request_start" : 0,
#                         "limit": 25,
#                         "offset_change": 10,
#                         "title_includes": "",
#                         "sleep_between_requests": 1
#                     }
                
#                 )
model_prep(parent_dir,output_dir)