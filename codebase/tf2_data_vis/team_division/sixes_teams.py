import pandas as pd
import re


def make_sixes_teams(rgl_info):
    team_dfs = make_team_dfs(rgl_info)
    sixes_teams_bad_division = filter_team_df(team_dfs)
    sixes_teams = filter_division_name(sixes_teams_bad_division)
    return sixes_teams



def make_team_dfs(rgl_info):
    rgl_df = pd.concat([pd.Series(rgl_info['id']),pd.Series(rgl_info['info'])],axis = 1)
    rgl_df.columns = ['steamid','info']
    no_profile = rgl_df[rgl_df['info'] == 'No Profile']
    profile = rgl_df.drop(no_profile.index)

    # Grab the first JSON in each tuple
    profile['rgl_profile'] = profile['info'].apply(lambda x: x[0].json())
    profile['teams'] = profile['info'].apply(lambda x: x[1].json())
    team_dfs = profile['teams'].apply(pd.json_normalize)

    team_dfs = pd.concat([profile['steamid'],team_dfs],axis = 1)
    return team_dfs


def filter_team_df(team_dfs):
   
    # Apply to the Series
    team_dfs['teams_id'] = team_dfs.apply(lambda row: add_steamid(row['teams'], row['steamid']), axis=1)

    team_df_list = team_dfs['teams_id'].to_list()

    rgl_teams = pd.concat(team_df_list)
    rgl_teams = rgl_teams[['steamid'] + [col for col in rgl_teams.columns if col != 'steamid']]
    sixes_teams = rgl_teams[rgl_teams['formatName'] == "Sixes"].copy()
    useful_cols = ['steamid', 'formatId', 'formatName', 'regionId', 'regionName','startedAt','leftAt','divisionId', 'divisionName',
        'teamId']
    sixes_teams_bad_divison = sixes_teams[useful_cols]
    return sixes_teams_bad_divison

def filter_division_name(sixes_teams_bad_division):

    # Make a copy to avoid SettingWithCopyWarning
    sixes_teams = sixes_teams_bad_division.copy()
    sixes_teams['divisionName'] = sixes_teams['divisionName'].str.lower()

    # Replacement mapping
    from_list = ['im/am', 'am/nc', 'adv', 'division one']
    to_list = ['amateur', 'newcomer', 'advanced', 'invite']

    # Replace using word boundaries
    for f, t in zip(from_list, to_list):
        pattern = r'\b' + re.escape(f) + r'\b'  # ensures exact match
        sixes_teams['divisionName'] = sixes_teams['divisionName'].str.replace(pattern, t, regex=True)
    divisions = ['amateur','main','intermediate','advanced','newcomer','invite']

    sixes_teams = sixes_teams[sixes_teams['divisionName'].isin(divisions)]
    return sixes_teams

def add_steamid(inner_df, steamid):
    inner_df = inner_df.copy()  # avoid modifying original in-place
    inner_df['steamid'] = steamid
    return inner_df
