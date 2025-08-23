from .manipulate_raw_data import * 
from .make_X_y import make_X_y
from .drop_bad_predictors import drop_bad_predictors
from .model_ready_data import make_model_ready_data_dict
import pandas as pd
import os
import joblib
from .bin_map_adjust_X import X_map_adj
def model_prep(parent_dir,output_dir):
    # Read data
    data_dict = read_data(parent_dir,output_dir)
    players = data_dict['players']
    info = data_dict['info']
    team_medic_stats = data_dict['team_medic_stats']
    teams = data_dict['teams']

    players_team_comp = team_class_comp(players = players)

    players_subset = short_matches(info = info, player_team_comp= players_team_comp,short_match_cutoff= 450)

    players_fixed_class_names = rename_scout_soldier(players_subset= players_subset)

    medic_players,combat_players = split_combat_medic(players_fixed_class_names,team_medic_stats)

    medic_wide,combat_wide = widen_data(medic_players,combat_players)

    players_wide = merge_wide_data(medic_wide,combat_wide,teams)

    X,y = make_X_y(players_wide)

    X = drop_bad_predictors(X)

    X = X.fillna(0)
    
    X_no_adj = X.copy()

    X,weights = X_map_adj(parent_dir,output_dir,X,y)
    X_no_adj['weights'] = weights.values

    model_ready_data_dict = make_model_ready_data_dict(players_wide,X_no_adj,y)
    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    print('dumping')
    joblib.dump(model_ready_data_dict,path)






