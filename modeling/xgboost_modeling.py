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

model_ready_data_dict = joblib.load('../data/pkls/model_ready_data_dict.pkl')
X = model_ready_data_dict['X']

cols = [col for col in X.columns if "cpcpm" in col]
X.drop(cols,axis = 1,inplace = True)


y = model_ready_data_dict['y']
seed = 123

# Set seeds
random.seed(seed)
np.random.seed(seed)


# Split into test and eval
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)


X_test, X_eval, y_test, y_eval = train_test_split(X_test, y_test, test_size=0.3)

# Set all the X datasets to have boolean columns
for name in ['X_train', 'X_test', 'X_eval']:
    df = eval(name)
    df = df.astype({col: bool for col in X.select_dtypes(include='object').columns})
    locals()[name] = df



# Define the base model
model = XGBClassifier(eval_metric='logloss', random_state=seed,
                      colsample_bytree = .3,subsample =.8)

#
search_space = {
    'max_depth': Integer(3, 15),
    'learning_rate': Real(0.01, 0.15, prior='log-uniform'),
    'n_estimators': Integer(500, 2500),
    'gamma': Real(0, 5),
    'reg_alpha': Real(0.1, 12, prior='log-uniform'),
    'reg_lambda': Real(0.1, 12, prior='log-uniform'),
    'min_child_weight': Integer(5, 40),
}

# Define cross-validation strategy
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

# Limit to 70% CPU
total_cores = multiprocessing.cpu_count()
n_jobs = int(total_cores * 0.70)

opt = BayesSearchCV(
    estimator=model,
    search_spaces=search_space,
    n_iter=200,                      # You can reduce this if it’s overheating
    scoring='accuracy',
    cv=cv,
    n_jobs=10,
    verbose=2,
    random_state=seed
)


opt.fit(X_train, y_train,)


joblib.dump(opt,'../data/pkls/opt.pkl')

best_model = opt.best_estimator_

print("BEST")
print(opt.best_params_)
print("BEST")

joblib.dump(best_model,'../data/pkls/xgb.pkl')
end = time.time()

length = round((( end - begin) / 60 ),2)
print(f'Took {length} Minutes')

print("Successfully dumped model to xgb.pkl")


os.system("shutdown /s /t 0")
