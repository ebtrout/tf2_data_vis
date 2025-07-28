import shap
import joblib
from sklearn.model_selection import train_test_split
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import percentileofscore
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# region Setup
# Read in Data 
model_ready_data_dict = joblib.load('../../data/pkls/model_ready_data_dict.pkl')
# Read in X sets
X = model_ready_data_dict['X']
X_train = model_ready_data_dict['X_train']
X_test = model_ready_data_dict['X_test']
X_eval = model_ready_data_dict['X_eval']

# Read in y sets
y = model_ready_data_dict['y']
y_train = model_ready_data_dict['y_train']
y_test = model_ready_data_dict['y_test']
y_eval = model_ready_data_dict['y_eval']

# Drop
X.drop('id',axis = 1,inplace = True)
X_train.drop('id',axis = 1,inplace = True)
X_test.drop('id',axis = 1,inplace = True)
X_eval.drop('id',axis = 1,inplace = True)

model = joblib.load('../../data/pkls/xgb.pkl')

# Set seeds
seed = 123
random.seed(seed)
np.random.seed(seed)

# endregiopn

# region Shap Explainer Sum by Class
explainer = shap.TreeExplainer(model)
class_name_list = ['scout','scout','soldier','soldier','medic','demoman']
num_list = ['1','2','1','2','','']


sum_by_class_list = []

for df in [X_test,X_eval,X]:
    shap_values = explainer.shap_values(df)

    shap_values = pd.DataFrame(shap_values)
    shap_values.columns = df.columns


    class_names = []

    shap_values_flip = shap_values.T.copy()

    for index in shap_values_flip.index:
        for class_name,num in zip(class_name_list,num_list):
            if index.startswith(class_name) and num in index:
                class_names.append(class_name + num)

    shap_values_flip['test'] = class_names

    sum_by_class = shap_values_flip.groupby('test').sum().T
    sum_by_class_list.append(sum_by_class)

# endregion

# Generate the shap value sums by class on test set
# Use those to generate the PIM's on the eval set by looking at the 
# Quantiles of the test set

# region Generate PIM

# function to use another series to generate quantiles
def get_quantile_series(reference_series, target_series):
    return target_series.apply(lambda x: percentileofscore(reference_series, x, kind='mean') / 100)

quantiled_df = pd.DataFrame({
    col: get_quantile_series(sum_by_class_list[0][col], sum_by_class_list[1][col])
    for col in sum_by_class_list[1].columns
})


quantile_X = pd.DataFrame({
    col: get_quantile_series(sum_by_class_list[0][col], sum_by_class_list[2][col])
    for col in sum_by_class_list[1].columns
})

PIM_X_eval = (quantiled_df * 10).round(2)

PIM_X = (quantile_X * 10).round(2)

PIM_X_eval['winner'] = y_eval.values

PIM_X['winner'] = y.values
print(PIM_X.groupby("winner").mean().round(2))

PIM_X.to_csv("../../data/PIM_X.csv",index = False)