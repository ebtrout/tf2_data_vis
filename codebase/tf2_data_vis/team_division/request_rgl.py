import requests
import time
from .steamid import steamid_list
from tf2_data_vis.get_log_data.batch import save_batch


def request_loop(sleep,parent_dir,output_dir,rgl_batches = None):
    steamids = steamid_list(parent_dir,output_dir)

    batch_counter = 1
    rgl_info = {
        "id": [],
        "info": []
    }
    # Load in batches and skip over already requested ids
    if type(rgl_batches) != type(None):
        steamids = [id for id in steamids if id not in rgl_batches['id']]
        batch_counter = int(len(rgl_batches['id']) / 100) + 1
    
    n = len(steamids)
    if n == 0:
        return
    
    for i,steamid in enumerate(steamids):

        if i % 100 == 0 or i == len(steamids) or i == len(steamids) -1:
            print(f'Requested {i} / {n} rgl profiles and team info')
            if i != 0 or ((n) == 1 and i == 0):
                save_batch(
                    batch = batch_counter,
                    parent_dir=parent_dir,
                    output_dir=output_dir,
                    batch_type= "rgl_info",
                    object = rgl_info
                )
                batch_counter += 1
                rgl_info = {
                "id": [],
                "info": []
            }
        
        
        info = request_rgl(steamid,sleep)
        rgl_info['id'].append(steamid)
        rgl_info['info'].append(info)


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