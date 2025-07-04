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

# Define the base model
model = XGBClassifier(eval_metric='logloss', random_state=seed)

# Define parameter grid to search over
param_grid = {
    'max_depth': np.arange(3, 7, 1),
    'learning_rate': np.arange(.01, .10, .01),
    'n_estimators': np.arange(100, 200, 10),
    'subsample': [.8],
    'colsample_bytree': [.75]
}

# Define cross-validation strategy
cv = StratifiedKFold(n_splits=6, shuffle=True, random_state=seed)

# Set up GridSearchCV   
grid_search = GridSearchCV(
    estimator=model,
    param_grid=param_grid,
    scoring='accuracy',   
    cv=cv,
    verbose=0,
    n_jobs=25
)

grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_


print(grid_search.best_params_)
joblib.dump(best_model,'../data/pkls/xgb.pkl')
end = time.time()

length = round((( end - begin) / 60 ),2)
print(f'Took {length} Minutes')

print("Successfully dumped model to xgb.pkl")
