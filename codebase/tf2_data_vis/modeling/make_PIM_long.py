    # read in
import os
import joblib
import pandas as pd
def make_PIM_long(parent_dir,output_dir):

    path = os.path.join(parent_dir,'..',output_dir,'pkls','model_ready_data_dict.pkl')
    model_ready_data_dict = joblib.load(path)
    X = model_ready_data_dict['X']
    players_wide = model_ready_data_dict['players_wide']



    path = os.path.join(parent_dir,'..',output_dir,'PIM_X.csv')
    PIM = pd.read_csv("../data/PIM_X.csv")
    path = os.path.join(parent_dir,'..',output_dir,'teams.csv')
    teams = pd.read_csv("../data/teams.csv")


    ### GET PLAYER CLASS NAMES TO BE STEAMID + SCOUT1 / SOLDIER2 / DEMO
    # Melt columns together to make a long dataset
    cols = ['id','team'] + [col for col in players_wide.columns if "steamid" in col]
    player_classes = players_wide[cols].copy()
    player_class_long = player_classes.melt(id_vars=['id', 'team'], 
                    var_name='class', 
                    value_name='steamiplayers_wided')

    # Make temp columns to transform 
    player_class_long['class_clean'] = player_class_long['class'].str.split("_").str[0]
    player_class_long['temp'] = player_class_long['class'].str.split("_").str[1]

    # Fix up class name to be scout1 soldier2 instead of just scout soldier
    class_list = []
    for i,name in enumerate(player_class_long['class_clean']):
        if name == 'scout' or name == 'soldier':
            name += player_class_long.loc[i,'temp']
        class_list.append(name)
    player_class_long['class'] = class_list
    player_class_long.drop(['class_clean','temp'],axis = 1,inplace = True)


    ### MAKE PIM BINDABLE
    PIM['id'] = X['id'].values


    PIM_long = PIM.melt(
        id_vars=['id', 'winner'],
        var_name='class',
        value_name='PIM'
    )

    # Make pim_long
    teams_pim = teams[['id','team','winner']].copy()
    PIM_long = PIM_long.merge(teams_pim,on = ['id','winner'],how = "left")
    PIM_long = PIM_long.merge(player_class_long,on = ['id','team','class'],how = 'left')
    PIM_long.rename(columns={"steamiplayers_wided":"steamid"},inplace = True)

    path = os.path.join(parent_dir,'..',output_dir,'PIM_X.csv')
    PIM_long.to_csv(path,index = False)