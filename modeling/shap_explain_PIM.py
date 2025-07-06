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
model_ready_data_dict = joblib.load('../data/pkls/model_ready_data_dict.pkl')
X = model_ready_data_dict['X']
y = model_ready_data_dict['y']

cols = [col for col in X.columns if "cpcpm" in col]
X.drop(cols,axis = 1,inplace = True)

model = joblib.load('../data/pkls/xgb.pkl')



# Set seeds
seed = 123
random.seed(seed)
np.random.seed(seed)


# Split into test and eval
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


X_test, X_eval, y_test, y_eval = train_test_split(X_test, y_test, test_size=0.3)

# endregiopn

# region Shap Explainer Sum by Class
explainer = shap.TreeExplainer(model)
class_name_list = ['scout','scout','soldier','soldier','medic','demoman']
num_list = ['1','2','1','2','','']


sum_by_class_list = []

for df in [X_test,X_eval]:
    shap_values = explainer.shap_values(df)

    shap_values = pd.DataFrame(shap_values)
    shap_values.columns = df.columns

   # shap_values.drop([col for col in shap_values.columns if col in valid_map_names],axis = 1,inplace = True)

    class_names = []

    shap_values_flip = shap_values.T.copy()

    for index in shap_values_flip.index:
        for class_name,num in zip(class_name_list,num_list):
            if class_name in index and num in index:
                class_names.append(class_name + num)
 #   shap_values.drop([col for col in shap_values.columns if col in valid_map_names],axis = 1,inplace = True)

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


PIM_df = (quantiled_df * 10).round(2)
PIM_df['winner'] = y_eval.values
print(PIM_df.groupby("winner").mean().round(2))

for col in PIM_df.columns:
    plt.hist(PIM_df[col],bins = 40,rwidth = .8, edgecolor = "black",color = "red")
    plt.show()


PIM_df.to_csv()