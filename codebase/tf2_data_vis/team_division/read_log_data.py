import pandas as pd
import os
def read_data(parent_dir,output_dir):
    data_dict = {}
    for f in ['players','info']:
        path = os.path.join(parent_dir,'..',output_dir,f + '.csv')
        df = pd.read_csv(path)
        data_dict[f] = df
    return data_dict