### SETUP ###
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
import random
import os
import time

begin = time.time()
os.chdir(os.path.dirname(os.path.abspath(__file__)))

model_ready_data_dict = joblib.load('../data/pkls/model_ready_data_dict.pkl')
X = model_ready_data_dict['X']
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
model = XGBClassifier(eval_metric='logloss', random_state=seed)

# Define parameter grid to search over
param_grid = {
    'max_depth': [7,10,15,20,None],
    'learning_rate': [.01],
    'n_estimators': np.arange(1400,1600,50),
    'gamma': [1],
    'reg_alpha': [.5],
    'reg_lambda': [1],
    'min_child_weight': np.arange(10,20,2),
    'subsample': [.8],
    'colsample_bytree': [.3]
}

# Define cross-validation strategy
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

# Set up GridSearchCV   
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    scoring='accuracy',   
    cv=cv,
    verbose=1,
    n_jobs=24
)

grid_search.fit(X_train, y_train,)

best_model = grid_search.best_estimator_


print(grid_search.best_params_)
joblib.dump(best_model,'../data/pkls/xgb.pkl')
end = time.time()

length = round((( end - begin) / 60 ),2)
print(f'Took {length} Minutes')

print("Successfully dumped model to xgb.pkl")
