import shap
import joblib
from sklearn.model_selection import train_test_split
import random
import numpy as np
import pandas as pd

# Read in Data 
model_ready_data_dict = joblib.load('../data/pkls/model_ready_data_dict.pkl')
X = model_ready_data_dict['X']
y = model_ready_data_dict['y']

model = joblib.load('../data/pkls/xgb.pkl')

# Set seeds
seed = 123
random.seed(seed)
np.random.seed(seed)


# Split into test and eval
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


X_test, X_eval, y_test, y_eval = train_test_split(X_test, y_test, test_size=0.3)

# Set all the X datasets to have boolean columns
for df in [X_train,X_test,X_eval]:
    df = df.astype({col: bool for col in X.select_dtypes(include='object').columns})


explainer = shap.TreeExplainer(model)

class_name_list = ['scout','scout','soldier','soldier','medic','demoman']
num_list = ['1','2','1','2','','']

stat_cols = [col for col in X.columns if any(col.contains(class_name) for class_name in class_name_list)]

valid_map_names = [col for col in X.columns if col not in stat_cols]

sum_by_class_list = []

for df in [X_test,X_eval]:
    shap_values = explainer.shap_values(df)

    shap_values = pd.DataFrame(shap_values)
    shap_values.columns = df.columns

    shap_values.drop([col for col in shap_values.columns if col in valid_map_names],axis = 1,inplace = True)

    class_names = []

    shap_values_flip = shap_values.T.copy()

    for index in shap_values_flip.index:
        for class_name,num in zip(class_name_list,num_list):
            if class_name in index and num in index:
                class_names.append(class_name + num)
    shap_values.drop([col for col in shap_values.columns if col in valid_map_names],axis = 1,inplace = True)

    shap_values_flip['test'] = class_names

    sum_by_class = shap_values_flip.groupby('test').sum().T
    sum_by_class_list.append(sum_by_class)