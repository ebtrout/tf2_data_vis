
import pandas as pd
import joblib
import os



def model_summary(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    model_ready_data_dict = joblib.load(path)
    # region SETUP

    path = os.path.join(parent_dir,'..',output_dir,'pkls','xgb.pkl')
    model = joblib.load(path)



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

    # Drop ids
    X_train.drop('id',axis = 1,inplace = True)
    X_test.drop('id',axis = 1,inplace = True)
    X_eval.drop('id',axis = 1,inplace = True)


    # endregion

    # region Make Model Summary
    print(model.get_params())

    importance = pd.Series(model.feature_importances_,name = "importance").round(4)
    feature_names = pd.Series(model.feature_names_in_,name = "name")
    summary = pd.concat([feature_names,importance],axis = 1).sort_values(by = 'importance',ascending=False)

    # Grab necessary vars
    score = model.score(X_test,y_test)

    # Assign values to dict 
    summary['score'] = round(score,4)

    summary['importance_relative'] = (summary['importance'] / summary['importance'].max()).round(2)

    path = os.path.join(parent_dir,'..',output_dir,'model_summary.csv')
    summary.to_csv(path,index = False)
    # endregion