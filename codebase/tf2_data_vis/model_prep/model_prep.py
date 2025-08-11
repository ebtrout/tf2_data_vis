from .team_class_comp import team_class_comp
from .short_matches import short_matches
from .rename_scout_soldier import rename_scout_soldier
from .split_combat_medic import split_combat_medic
from .widen_data import widen_data
from .merge_wide_data import merge_wide_data
from .make_X_y import make_X_y
from .drop_bad_predictors import drop_bad_predictors
from .model_ready_data import model_ready_data
from .read_data import read_data
import pandas as pd
import os
import joblib
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

    model_ready_data_dict = model_ready_data(players_wide,X,y)
    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    print('dumping')
    joblib.dump(model_ready_data_dict,path)






