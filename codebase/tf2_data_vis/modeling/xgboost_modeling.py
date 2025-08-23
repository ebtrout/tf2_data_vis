import numpy as np
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import  StratifiedKFold
import random
import os
import time
from skopt import BayesSearchCV
from skopt.space import Real, Integer

def xgboost_modeling(parent_dir,output_dir,skip_model = False):
    if skip_model == True:
        print("Skipping modeling and reading from a file assuming modeling has already been done")
        return
    seed = 123

    # Set seeds
    random.seed(seed)
    np.random.seed(seed)
    
    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    model_ready_data_dict = joblib.load(path)
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

    weights_train = X_train['weights']
    weights_test = X_test['weights']
    weights_eval = X_eval['weights']

    # Drop
    X_train.drop(['weights','id'],axis = 1,inplace = True)
    X_test.drop(['weights','id'],axis = 1,inplace = True)
    X_eval.drop(['weights','id'],axis = 1,inplace = True)



    # Set all the X datasets to have boolean columns
    for name in ['X_train', 'X_test', 'X_eval']:
        df = eval(name)
        df = df.astype({col: bool for col in X.select_dtypes(include='object').columns})
        locals()[name] = df

    # Define the base model
    model = XGBClassifier(eval_metric='logloss', random_state=seed,
                        colsample_bytree = .30,subsample =.8,
                        learning_rate = .1,
                        min_child_weight = int(.005 * len(X_train)))

    #
    search_space = {
        'max_depth': Integer(3, 8),
        'n_estimators': Integer(2000, 7000),
        'gamma': Real(0, 5),
        'reg_alpha': Real(0.1,5, prior='log-uniform'),
        'reg_lambda': Real(0.1, 5, prior='log-uniform'),

    }

    # Define cross-validation strategy
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)

    # Limit to 70% CPU

    full_fit = BayesSearchCV(
        estimator=model,
        search_spaces=search_space,
        n_iter=50,                      # You can reduce this if it’s overheating
        scoring='accuracy',
        cv=cv,
        verbose=2,
        random_state=seed
    )

    begin = time.time()

    full_fit.fit(X_train, y_train,sample_weight = weights_train)


    path = os.path.join(parent_dir,'..',output_dir,'pkls','full_fit.pkl')
    joblib.dump(full_fit,path)

    best_model = full_fit.best_estimator_

    print("BEST")
    print(full_fit.best_params_)
    print("BEST")

    path= os.path.join(parent_dir,'..',output_dir,'pkls','xgb.pkl')
    joblib.dump(best_model,path)

    end = time.time()

    length = round((( end - begin) / 60 ),2)
    print(f'Took {length} Minutes')

    print("Successfully dumped model to xgb.pkl")

