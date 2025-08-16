from tf2_data_vis.get_log_data.get_log_data import *
from tf2_data_vis.model_prep.model_prep import model_prep
from tf2_data_vis.modeling.modeling import modeling
from tf2_data_vis.vis_prep.vis_prep import vis_prep
import os

parent_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = 'data'

# Run this to get all data used for the tableau dashboard
# THIS WILL TAKE > 10 HOURS!!!!
# THIS WILL TAKE > 10 HOURS!!!!
# THIS WILL TAKE > 10 HOURS!!!!
# Requests > 2.2M logs and subsets them down 
# output_dir = 'data'
###
# get_log_data(
#                     batch_size = 100,
#                     request_ids = True,
#                     request_data = True,
#                     filter_logs = True,
#                     update_log_ids = True,
#                     output_dir = output_dir,
#                     manipulate_log_data = True,
#                     parent_dir = parent_dir,
#                     debug = False,
#                     request_params = {
#                         "n": 2500,
#                         "cutoff_date": '2016-07-07',
#                         "request_start" : 0,
#                         "limit": 1000,
#                         "offset_change": 1000,
#                         "title_includes": "",
#                         "sleep_between_requests": 1
#                     }
                
#                 )

# get_log_data(
#                     batch_size = 100,
#                     request_ids = False,
#                     request_data = False,
#                     filter_logs = True,
#                     update_log_ids = True,
#                     output_dir = output_dir,
#                     parent_dir = parent_dir,
#                     manipulate_log_data = True,
#                     debug = False,
#                     request_params = {
#                         "n": 5,
#                         "cutoff_date": '2016-07-07',
#                         "request_start" : 0,
#                         "limit": 1000,
#                         "offset_change": 1000,
#                         "title_includes": "",
#                         "sleep_between_requests": 1
#                     }
                
#                 )

model_prep(parent_dir,output_dir)

modeling(parent_dir=parent_dir,output_dir=output_dir,skip_model= False)
 
vis_prep(parent_dir=parent_dir,output_dir=output_dir)
