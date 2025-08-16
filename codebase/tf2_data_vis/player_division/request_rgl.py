import requests
import time
from .steamid import steamid_list
from tf2_data_vis.get_log_data.batch import save_batch


def request_loop(sleep,parent_dir,output_dir):
    steamids = steamid_list(parent_dir,output_dir)

    batch_counter = 1
    n = len(steamids)
    rgl_info = {
        "id": [],
        "info": []
    }
    for i,steamid in enumerate(steamids):

        if i % 100 == 0:
            print(f'Requested {i} / {n} rgl profiles and team info')
            if i != 0:
                save_batch(
                    batch = batch_counter,
                    parent_dir=parent_dir,
                    output_dir=output_dir,
                    batch_type= "rgl_info",
                    object = rgl_info
                )
                rgl_info = {
                "id": [],
                "info": []
            }
        
        
        info = request_rgl(steamid,sleep)
        rgl_info['id'].append(steamid)
        rgl_info['info'].append(info)
        if i > 2:
            break
    
    return rgl_info


def request_rgl(steamid,sleep):
    time.sleep(sleep)
    profile = request_profile(steamid)
    if profile.status_code == 404:
        return "No Profile"
    time.sleep(sleep)
    teams = request_teams(steamid)
    return profile,teams


def request_profile(steamid):
    url = f'https://api.rgl.gg/v0/profile/{steamid}'

    response = requests.get(url)
    return response

def request_teams(steamid):
    url = f'https://api.rgl.gg/v0/profile/{steamid}/teams'

    response = requests.get(url)
    return response