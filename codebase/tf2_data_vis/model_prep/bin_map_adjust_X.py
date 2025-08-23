from optbinning import OptimalBinning
import warnings
import pandas as pd
from sklearn.model_selection import KFold
from pandas.errors import PerformanceWarning
import os
import joblib
import numpy as np
import random

def X_map_adj(parent_dir,output_dir,X,y):
    data_dict = read_data(parent_dir,output_dir)
    info = data_dict['info']
    teams = data_dict['teams']
    team_divisions = data_dict['team_divisions']

    X_pre_bin,weights = pre_bin(team_divisions,teams,X,y)
    X_binned = bin_X(X_pre_bin,y,weights)
    X_map_adj_df = encode_X_by_map(X_binned,info,X,y)
    X_map_adj_df['id'] = X['id'].copy()
    return X_map_adj_df,weights

def pre_bin(team_divisions,teams,X,y):
    team_divisions = team_divisions.merge(teams[['id','team','winner']],on = ['id','team'])
    X_pre_bin = X.copy()
    X_pre_bin['winner'] = y

    X_pre_bin  = X_pre_bin.merge(team_divisions[['id','winner','division_weight']],on = ['id','winner'])
    weights = X_pre_bin['division_weight'].copy()
    X_pre_bin = X_pre_bin.drop(['id','winner','division_weight'],axis=1)
    return X_pre_bin,weights

def bin_X(X_pre_bin,y,weights):
    warnings.filterwarnings("ignore", category=FutureWarning)
    problem =[]
    X_binned = pd.DataFrame()
    for col in X_pre_bin.columns:
        try:    
            optb = OptimalBinning(
                max_n_bins=5,
                name = col,
                min_bin_size = .05,
                
            )
            optb.fit(X_pre_bin[col],y,sample_weight=weights)
            binned_col = optb.transform(x = X_pre_bin[col],metric = "bins")
            X_binned = X_binned.copy()
            X_binned[col] = binned_col

        except Exception as e:
            problem.append(col)
    return X_binned

def encode_X_by_map(X_binned,info,X,y):
    X_exploded = pd.get_dummies(X_binned).copy()
    X_exploded['win'] = y.copy()
    X_exploded['id'] = X['id'].copy()
    X_exploded = X_exploded.merge(info[['id','clean_map_name']])

    # Example usage:
    feature_cols = [col for col in X_exploded.columns if col not in ['id', 'clean_map_name', 'win']]
    df_map_adjusted = conditional_target_encoding_vectorized(X_exploded, feature_cols, map_col='clean_map_name', target_col='win', id_col='id', n_splits=5)
    warnings.filterwarnings("ignore", category=PerformanceWarning)
    final_df = pd.DataFrame()
    df_map_adjusted.to_csv("wow.csv")
    X_binned.to_csv("wow2.csv")
    for col in X_binned.columns:
            
        binned_cols = [bins for bins in df_map_adjusted.columns if col in bins]
        collected_column = df_map_adjusted[binned_cols].T.sum()
        final_df[col + "_map_adj"] = collected_column.copy()
    return final_df



def conditional_target_encoding_vectorized(df, feature_cols, map_col='clean_map_name',
                                           target_col='win', id_col='id',
                                           n_splits=5, smoothing=5):
    warnings.filterwarnings("ignore")
    
    # Initialize output with identifier columns
    df_encoded = df[[id_col, map_col, target_col]].copy()
    
    # Prepare empty columns for map-adjusted features
    for feature in feature_cols:
        df_encoded[feature + '_map_adj'] = 0.0
    
    # Shuffle indices
    np.random.seed(100)
    random.seed(100)
    indices = np.random.permutation(df.index)
    
    # Create folds
    fold_sizes = np.full(n_splits, len(df) // n_splits)
    fold_sizes[:len(df) % n_splits] += 1
    val_list = []
    start = 0
    for size in fold_sizes:
        end = start + size
        val_list.append(indices[start:end])
        start = end
    train_list = [np.setdiff1d(indices, val_idx) for val_idx in val_list]
    
    # Collect per-fold feature DataFrames
    fold_encoded_list = []
    
    for train_idx, val_idx in zip(train_list, val_list):
        train, val = df.iloc[train_idx], df.iloc[val_idx]
        
        # Compute global feature-bin win rates for smoothing
        global_rates = train[feature_cols].multiply(train[target_col], axis=0).sum() / train[feature_cols].sum()
        
        val_fold_features = pd.DataFrame(index=val.index)
        
        for feature in feature_cols:
            train_feat = train[train[feature] == 1]
            map_feat_stats = train_feat.groupby(map_col)[target_col].agg(['mean','count']).reset_index()
            
            # Smoothed map-adjusted rate
            map_feat_stats['smoothed'] = (
                (map_feat_stats['count']*map_feat_stats['mean'] + smoothing*global_rates[feature]) /
                (map_feat_stats['count'] + smoothing)
            )
            
            val_feat = val[[feature, map_col]].merge(map_feat_stats[[map_col,'smoothed']],
                                                     on=map_col, how='left')
            val_feat['smoothed'] = val_feat['smoothed'].fillna(global_rates[feature])
            
            # Only apply to active feature rows
            val_fold_features[feature + '_map_adj'] = val_feat['smoothed'] * val_feat[feature]
        
        fold_encoded_list.append(val_fold_features)
    
    # Combine all folds and sort by original index
    df_encoded_features = pd.concat(fold_encoded_list).sort_index()
    
    # Merge with identifier columns
    df_encoded = pd.concat([df[[id_col, map_col, target_col]], df_encoded_features], axis=1)
    
    # Optional: save debug info
    joblib.dump(fold_encoded_list, 'folds_map_adjusted_debug.pkl')
    
    return df_encoded

def read_data(parent_dir,output_dir):
    data_dict = {}
    for f in ['info','teams','team_divisions']:
        path = os.path.join(parent_dir,'..',output_dir,f + '.csv')
        df = pd.read_csv(path)
        data_dict[f] = df
    return data_dict