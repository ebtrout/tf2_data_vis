from .request_rgl import request_loop
from tf2_data_vis.get_log_data.batch import join_rgl_info_batch
from .sixes_teams import make_sixes_teams
from .merge_onto_players import make_team_divison
from .read_log_data import read_data
import os

def team_division(parent_dir,output_dir):
    rgl_batches = join_rgl_info_batch(parent_dir=parent_dir,output_dir=output_dir,batch_type='rgl_info')
    request_loop(sleep = .5,
                 parent_dir= parent_dir,
                 output_dir= output_dir,
                 rgl_batches=rgl_batches)
    rgl_info = join_rgl_info_batch(parent_dir=parent_dir,
                                   output_dir=output_dir,
                                   batch_type='rgl_info')
    sixes_teams = make_sixes_teams(rgl_info)

    log_data_dict = read_data(parent_dir,output_dir)
    players = log_data_dict['players']
    info = log_data_dict['info']
    team_division_df = make_team_divison(players,sixes_teams,info)
    path = os.path.join(parent_dir,'..',output_dir,'team_divisions.csv')
    team_division_df.to_csv(path,index = False)
