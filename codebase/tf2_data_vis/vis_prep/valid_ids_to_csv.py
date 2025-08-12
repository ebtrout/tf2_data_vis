import os
import joblib
import pandas as pd
def valid_ids_to_csv(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    model_ready_data_dict = joblib.load(path)

    valid_ids = model_ready_data_dict['ids']
    valid_ids = valid_ids.unique()
    valid_ids = pd.Series(valid_ids,name = 'id')

    path = os.path.join(parent_dir,'..',output_dir,'valid_ids.csv')

    valid_ids.to_csv(path,index = False)