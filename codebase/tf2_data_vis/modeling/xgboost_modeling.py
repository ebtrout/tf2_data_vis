### SETUP ###
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
import random
import os
import multiprocessing
import time
from skopt import BayesSearchCV
from skopt.space import Real, Integer


begin = time.time()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
X_train.drop('id',axis = 1,inplace = True)
X_test.drop('id',axis = 1,inplace = True)
X_eval.drop('id',axis = 1,inplace = True)

seed = 123

# Set seeds
random.seed(seed)
np.random.seed(seed)


# Set all the X datasets to have boolean columns
for name in ['X_train', 'X_test', 'X_eval']:
    df = eval(name)
    df = df.astype({col: bool for col in X.select_dtypes(include='object').columns})
    locals()[name] = df



# Define the base model
model = XGBClassifier(eval_metric='logloss', random_state=seed,
                      colsample_bytree = .25,subsample =.8)

#
search_space = {
    'max_depth': Integer(3, 8),
    'learning_rate': Real(0.01, 0.05, prior='log-uniform'),
    'n_estimators': Integer(1000, 5000),
    'gamma': Real(0, 5),
    'reg_alpha': Real(0.1,5, prior='log-uniform'),
    'reg_lambda': Real(0.1, 5, prior='log-uniform'),
    'min_child_weight': Integer(25,40),
}

# Define cross-validation strategy
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

# Limit to 70% CPU
total_cores = multiprocessing.cpu_count()
n_jobs = int(total_cores * 0.70)

opt = BayesSearchCV(
    estimator=model,
    search_spaces=search_space,
    n_iter=100,                      # You can reduce this if it’s overheating
    scoring='accuracy',
    cv=cv,
    n_jobs=7,
    verbose=2,
    random_state=seed
)


opt.fit(X_train, y_train,)


joblib.dump(opt,'../../data/pkls/opt.pkl')

best_model = opt.best_estimator_

print("BEST")
print(opt.best_params_)
print("BEST")

joblib.dump(best_model,'../../data/pkls/xgb.pkl')
end = time.time()

length = round((( end - begin) / 60 ),2)
print(f'Took {length} Minutes')

print("Successfully dumped model to xgb.pkl")

