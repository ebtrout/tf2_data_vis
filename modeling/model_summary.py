
import random
import numpy as np
from sklearn.model_selection import train_test_split
import pandas as pd
import joblib
import os
# Set seeds
seed = 123
random.seed(seed)
np.random.seed(seed)

os.chdir(os.path.dirname(os.path.abspath(__file__)))



model_ready_data_dict = joblib.load('../data/pkls/model_ready_data_dict.pkl')
X = model_ready_data_dict['X']
y = model_ready_data_dict['y']

# Split into test and eval
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

X_test, X_eval, y_test, y_eval = train_test_split(X_test, y_test, test_size=0.3)

model = joblib.load("../data/pkls/xgb.pkl")

importance = pd.Series(model.feature_importances_,name = "importance")
feature_names = pd.Series(model.feature_names_in_,name = "name")
summary = pd.concat([feature_names,importance],axis = 1).sort_values(by = 'importance',ascending=False)

# Grab necessary vars
score = model.score(X_eval,y_eval)
probs = model.predict_proba(X_test)
probs = (probs[:,1])

# Assign values to dict 
summary['score'] = score

summary['importance_relative'] = summary['importance'] / summary['importance'].max()

print(summary)