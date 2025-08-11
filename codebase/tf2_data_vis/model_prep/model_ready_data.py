from sklearn.model_selection import train_test_split
import random
import numpy as np

def model_ready_data(players_wide,X,y):
    random.seed(123)
    np.random.seed(123)
    ids = players_wide['id']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=123)

    X_test, X_eval, y_test, y_eval = train_test_split(X_test, y_test, test_size=0.3,random_state=123)

    model_ready_data_dict = {
        'X':X,
        'X_train':X_train,
        'X_test':X_test,
        'X_eval':X_eval,
        'y':y,
        'y_train':y_train,
        'y_test':y_test,
        'y_eval':y_eval,
        'ids': ids,
        "players_wide":players_wide,        
    }

    return model_ready_data_dict
