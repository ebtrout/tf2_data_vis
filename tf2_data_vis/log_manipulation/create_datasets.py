import pandas as pd
import numpy as np
from pandas import json_normalize

# Initialize each of the major datasets from the keys of the log JSON
# Medic+stats, class_stats, and round_events are created 
# From their respective parent dataset

## INFO ##
def info(log,id):
    map = log['info']['map']
    title = log['info']['title']
    length = log['length']
    date = log['info']['date']


    info = pd.DataFrame({'id': [id], 'length': [length], 'map': [map],'title':[title],'date':[date]})
    info['date'] = pd.to_datetime(info['date'], unit='s')

    return(info)

def players(log):
    
    # Shape players to be usable
    players = json_normalize(log['players'])
    players = players.T
    players['stats'] = players[0]
    players.drop(columns=[0], inplace=True)
    players.reset_index(inplace=True)
    players[['steamid', 'metric']] = players['index'].str.extract(r'(\[U:1:\d+\])(?:\.(.*))?')

    # Drop where player steam id is NA
    players = players[players['steamid'].notna()]

    # Pivot so there are multiple columns per row
    players = players.pivot(index = 'steamid', columns='metric', values='stats')

    # Drop useless columns
    drop_cols = ['as','backstabs','headshots','headshots_hit','lks','ic']
    drop_cols = [col for col in drop_cols if col in players.columns]
    players.drop(drop_cols,axis = 1,inplace = True)

    # Create ka 
    for col in ['kills','assists']:
        if col not in players.columns:
            players[col] = pd.Series(dtype = 'int')
    
    players['ka'] = players['kills'] + players['assists']

    players.reset_index(inplace=True)
    players.rename(columns={'index':'steamid'},inplace = True)
    return(players)

## REQUIRES PLAYERS!! ##
def medic_stats(players):
    
    # Separate medic stats and player stats
    colnames = players.columns
    colnames = [col for col in colnames if "medi" not in col and "uber" not in col and "drops"]

    medic_stats = players[[col for col in players.columns if col not in colnames] + ['steamid']]
    players = players[colnames]

    return(players,medic_stats)

## REQUIRES PLAYERS!! ##
def class_stats(players):

    # region Class Stats
    class_stats = pd.DataFrame()
    for i in range(0,len(players)):
        player_class =  pd.DataFrame(players.loc[players.index[i],'class_stats'])
        player_class = player_class[player_class['type'] != 'undefined']
        player_class['steamid'] = players['steamid'].values[i]
        
        class_stats = pd.concat([class_stats, player_class], ignore_index=True)
        
    # Grab Weapon Stats
    #weapon = class_stats[['weapon','steamid','type']].copy()
    if 'weapon' in class_stats.columns:
        class_stats.drop('weapon',axis = 1,inplace = True)

    # Check if class_stats is null??
    if len(class_stats) > 0:
        class_stats = class_stats[['steamid'] + [col for col in class_stats.columns if col != 'steamid']]

        class_stats['total_time'] = class_stats['total_time'].abs()

        time_alive = class_stats.groupby('steamid').agg(time = ("total_time","sum")).reset_index()

        class_stats = class_stats.merge(time_alive)

        class_stats.rename(columns = {'time':'total_time',"total_time":"class_time"},inplace = True)

        # Drop the 'class_stats' column from players DataFrame
        players.drop('class_stats',axis = 1,inplace = True)
    return players, class_stats

def teams(log):
    ## TEAMS ## 

    # Shape teams
    teams = json_normalize(log['teams']).T.reset_index()
    teams[['team','metric']] = teams['index'].str.extract(r'(\w+)(?:\.(.*))?')
    teams.drop(columns=['index'], inplace=True)

    # Pivot to have multiple cols
    teams = teams.pivot(index='team', columns='metric', values=0)
    teams = teams.replace(0,np.nan)

    # Make drop_rate
    teams['drop_rate'] = teams['drops'].div(teams['charges']).astype(float).round(4)
    teams.reset_index(inplace = True)

    return teams

def rounds(log):
    ## ROUNDS ##
    # region Rounds
    rounds = json_normalize(log['rounds'])

    colnames = rounds.columns.str.contains('players')
    rounds = rounds[rounds.columns[~colnames]]
    
    # Drop  rounds with no winner, and short rounds
    rounds.dropna(subset=['winner'], inplace=True)
    rounds = rounds[rounds['length'] > 40]

    rounds.reset_index(inplace=True)
    rounds.rename(columns={"index":"round"},inplace = True)

    return rounds

## REQUIRES ROUNDS!!! ## 
def round_events(rounds):
    ## ROUND EVENTS ## 
    round_events_temp = rounds['events']

    round_events = pd.DataFrame()
    for i in range(0,len(round_events_temp)):
        round_event =  pd.DataFrame(round_events_temp.loc[i])
        round_event['round'] = i
        round_events = pd.concat([round_events, round_event], ignore_index=True)

    # Change order to have round as first column
    cols = ['round'] + [col for col in round_events.columns if col != 'round']

    round_events = round_events[cols]

    rounds.drop('events',axis =1,inplace= True)
    rounds.drop_duplicates(inplace= True)

    return rounds, round_events

def player_rounds(log,players):

    # Subsetting cols
    player_rounds = json_normalize(log['rounds']).drop('events',axis =1)
    colnames = player_rounds.columns.str.contains('players')
    player_rounds = player_rounds[player_rounds.columns[colnames]]
    player_rounds = player_rounds.T

    # Fixing index
    player_rounds.index = player_rounds.index.str.replace('players.','')
    player_rounds.reset_index(inplace=True)

    # Reshaping
    player_rounds[['steamid','metric']] = player_rounds['index'].str.extract(r'(\[.*\]).(.*)')

    # Melt into long format
    value_vars = [col for col in player_rounds.columns if col not in ['steamid','index','metric']]
    long_df = player_rounds.melt(
        id_vars=['steamid', 'metric'],
        value_vars=value_vars,
        var_name='round',
        value_name='value'
    )
    long_df = long_df[long_df['steamid'].notna()]

    # Pivot to get the desired format
    player_rounds = long_df.pivot(index = ['steamid','round'], columns='metric', values='value').reset_index()
    
    names = players[['steamid','name']].copy()

    player_rounds = player_rounds.merge(names, on = ['id','steamid'])

    return player_rounds

def healspread(log,players):
    # Turn steamid.steamid cols to healer and healed
    healspread = json_normalize(log['healspread']).T.reset_index()

    healspread.rename(columns={0: 'value'}, inplace=True)
    colnames = healspread['index'].str.split('.')

    healspread['healer'] = colnames.str[0]
    healspread['healed'] = colnames.str[1]

    healspread.drop('index', axis=1, inplace=True)

    healspread = healspread[['healer', 'healed', 'value']]
    
    # bind in useful player information
    healspread['steamid'] = healspread['healer'].copy()

    players_info = players[['steamid','team','name','primary_class']].copy()

    players_info.columns = ['steamid','team','medic_name','primary_class']

    healspread = healspread.merge(players_info,on = ['steamid'])

    healspread.drop('primary_class',axis = 1,inplace= True)

    healspread['steamid'] = healspread['healed'].copy()

    players_info.drop('team',axis = 1,inplace = True)
    players_info.columns = ['steamid', 'healed_name', 'primary_class']

    healspread = healspread.merge(players_info,on = ['steamid'])

    healspread.drop('steamid',axis = 1,inplace = True)

    return healspread

def healspread_grouped(log,players):
    
    healspread = json_normalize(log['healspread']).T.reset_index()

    healspread.rename(columns={0: 'value'}, inplace=True)
    colnames = healspread['index'].str.split('.')

    healspread['healer'] = colnames.str[0]
    healspread['healed'] = colnames.str[1]

    healspread.drop('index', axis=1, inplace=True)

    healspread = healspread[['healer', 'healed', 'value']]
    healspread = healspread.copy()
    ## Healspread ##
    # region Healspread By Class
    healspread['steamid'] = healspread['healed']

    healspread = healspread.merge(players[['steamid','primary_class','team']])

    healspread.groupby(['team', 'primary_class']).agg(
        value=('value', 'sum'),
    ).reset_index()

    total_heal = healspread.groupby(['team']).agg(
        total_heal = ('value', 'sum'),
    )

    healspread = healspread.merge(total_heal, on='team', how='left')

    # Avoid divide by zero
    healspread = healspread.replace(0,np.nan)

    healspread['pct_heal'] = healspread['value'].div(healspread['total_heal']).astype(float).round(4)

    healspread.drop(['total_heal','healed','healer','steamid'],axis=1, inplace=True)

    healspread = healspread.groupby(['team', 'primary_class']).agg(
        heals=('value', 'sum'), 
        pct_heal=('pct_heal', 'mean')
    ).reset_index()

    healspread.rename(columns={'value': 'heals','primary_class':'class'}, inplace=True)

    healspread = healspread[['team','class','heals','pct_heal']]

    healspread_red = healspread[healspread['team'] == 'Red'].pivot(index='team', columns='class', values=['heals', 'pct_heal'])

    healspread_red.columns = [f'{col[1]}_{col[0]}' for col in healspread_red.columns if col[0] != 'team']

    healspread_blue = healspread[healspread['team'] == 'Blue'].pivot(index='team', columns='class', values=['heals', 'pct_heal'])

    healspread_blue.columns = [f'{col[1]}_{col[0]}' for col in healspread_blue.columns if col[0] != 'team']

    #healspread_blue = healspread_blue[healspread_red.columns]

    healspread = pd.concat([healspread_red, healspread_blue], axis=0)

    return healspread

def class_kda(log):
     ## CLASS KDA ##
    # region Class KDA

    # Class Kills
    class_kills = json_normalize(log['classkills']).T.reset_index()

    class_kills.rename(columns={0: 'value'}, inplace=True)

    colnames = class_kills['index'].str.split('.')

    class_kills['steamid'] = colnames.str[0]
    class_kills['killed'] = colnames.str[1]

    class_kills.drop('index', axis=1, inplace=True)

    class_kills = class_kills.pivot(index='steamid', columns='killed', values='value').reset_index()

    class_kills.replace({np.nan: 0}, inplace=True)

    colnames = class_kills.columns

    colnames = [col + '_kills' for col in colnames if col != 'steamid']

    colnames = ['steamid'] + colnames

    class_kills.columns = colnames

    # Class Deaths
    class_deaths = json_normalize(log['classdeaths']).T.reset_index()

    class_deaths.rename(columns={0: 'value'}, inplace=True)

    colnames = class_deaths['index'].str.split('.')

    class_deaths['steamid'] = colnames.str[0]
    class_deaths['died_to'] = colnames.str[1]

    class_deaths.drop('index', axis=1, inplace=True)

    class_deaths = class_deaths.pivot(index='steamid', columns='died_to', values='value').reset_index()

    class_deaths.replace({np.nan: 0}, inplace=True)

    colnames = class_deaths.columns

    colnames = [col + '_deaths' for col in colnames if col != 'steamid']

    colnames = ['steamid'] + colnames

    class_deaths.columns = colnames

    # Class Assists

    class_assists = json_normalize(log['classkillassists']).T.reset_index()

    class_assists.rename(columns={0: 'value'}, inplace=True)

    colnames = class_assists['index'].str.split('.')

    class_assists['steamid'] = colnames.str[0]
    class_assists['assisted'] = colnames.str[1]

    class_assists.drop('index', axis=1, inplace=True)

    class_assists = class_assists.pivot(index='steamid', columns='assisted', values='value').reset_index()

    class_assists.replace({np.nan: 0}, inplace=True)

    colnames = class_assists.columns

    colnames = [col + '_assists' for col in colnames if col != 'steamid']

    colnames = ['steamid'] + colnames

    class_assists.columns = colnames

    # Merge into KDA

    class_kda = class_kills.merge(class_deaths, on='steamid', how='right')
    class_kda = class_kda.merge(class_assists, on='steamid', how='right')

    return class_kda

def push_statistics(round_events,rounds_df,teams_df):
    ## PUSH STATS ##

    ## NOT SURE IF NEEDED #### 

    # Changing round_events names
    invert_team = pd.Series(["Red","Blue"],index = ['Blue','Red'])

    wins = round_events[round_events['type'].isin(["pointcap","round_win"])]

    wins = wins[wins["round"] == 0].reset_index()

    winning_team = wins.loc[len(wins) - 2]['team']
    winning_point = wins.loc[len(wins) - 2]['point']

    # Decide how to loop throuhg point numbers
    point_names = {}
    loop_list = []
    if winning_point == 1.0:
        loop_list = [1.0,2.0,3.0,4.0,5.0]
    elif winning_point == 5.0:
        loop_list = [5.0,4.0,3.0,2.0,1.0]

    # Change point names based on team winner
    for i,point in enumerate(loop_list):
        s = ""
        if i == 0:
            team = invert_team[winning_team]
            s = f'{team}_Last'
        elif i == 1:
            team = invert_team[winning_team]
            s = f'{team}_Second'
        elif i == 2:
            s = f'Mid'
        elif i == 3:
            team = winning_team
            s = f'{team}_Second'
        elif i == 4:
            team = winning_team
            s = f'{team}_Last'
        point_names[point] = s


    # #### NOT SURE IF NEEDED

    # point_names = {
    #     1.0: 'Blue_Last',
    #     2.0: 'Blue_Second',
    #     3.0: 'Mid',
    #     4.0: 'Red_Second',
    #     5.0: 'Red_Last'
    # }


    # Change pointnames
    push = round_events[round_events['type'].isin(["pointcap"])].copy()
    if len(push) == 0:
        push['point'] = pd.Series(dtype = 'float')
    push['point'] = [point_names[point] for point in push['point']]

    # Push Types
    pushes = pd.DataFrame(columns=['count','time'])

    for num in push['round'].unique():
        round_pushes = push[push['round'] == num].copy().reset_index(drop=True)

        for i in range(len(round_pushes) - 1):  # no need to go to last index
            team = round_pushes.loc[i, "team"]

            # Create the row index
            point1 = round_pushes.loc[i, 'point']
            point2 = round_pushes.loc[i + 1, 'point']
            next_team = round_pushes.loc[i + 1, 'team']
            row = f'{next_team}: {point1} - {point2}'

            # Calculate time for the event
            time_for_event = round_pushes.loc[i+1,'time'] - round_pushes.loc[i,'time']

            # Initialize the row if it's not already present
            if row not in pushes.index:
                pushes.loc[row] = {'count': 0,'time':0}
            
            # Add in values
            pushes.loc[row, 'count'] += 1
            pushes.loc[row, 'time'] += time_for_event

    # Avoid Divide by Zero
    pushes = pushes.replace(0,np.nan)
    # Create average time per push type
    pushes['av_time'] = pushes['time'].div(pushes['count']).astype(float).round(4)


    # Transforming Push Types
    colnames = ["push_mid",'takeback_mid','push_last','defend_last','push_second','takeback_enemy_second']
    colnames = colnames + [col + '_time' for col in colnames]
    push_df = pd.DataFrame(index = ['Red','Blue'],columns = colnames)

    # Loop through and make events readable
    for i,index in enumerate(pushes.index):
        # Split and initialize
        l = (index.split(" "))
        value = pushes.loc[index,'count']
        time = pushes.loc[index,'av_time']
        team = l[0].strip(":")
        point = l[1]
        next_point = l[3]

        # If the point is taken back
        if point == next_point:
            if point == "Mid":
                push_df.loc[team,"takeback_mid"] = value
                push_df.loc[team,"takeback_mid_time"] = time

            if "Second" in point:
                if team in point:
                    push_df.loc[team,"defend_last"] = value
                    push_df.loc[team,"defend_last_time"] = time
                else:
                    push_df.loc[team,"takeback_enemy_second"] = value
                    push_df.loc[team,"takeback_enemy_second_time"] = time
        # If the point is pushed onto
        else:
            if "Second" in point and "Last" in next_point:
                push_df.loc[team,"push_last"] = value
                push_df.loc[team,"push_last_time"] = time
            elif "Mid" in point and "Second" in next_point:
                push_df.loc[team,"push_second"] = value
                push_df.loc[team,"push_second_time"] = time
            elif "Second" in point and "Mid" in next_point:
                push_df.loc[team,"push_mid"] = value
                push_df.loc[team,"push_mid_time"] = time              


    # Calculating push rates
    push_df['push_last_fails'] = push_df['defend_last'].values.tolist()[::-1]
    push_df['push_second_fails'] = push_df['takeback_mid'].values.tolist()[::-1]


    # Avoid divide by zero
    push_df = push_df.replace(0,np.nan)

    push_df['convert_last_rate'] = push_df['push_last'].div(
        push_df['push_last_fails'] + push_df['push_last']
    ).astype(float).round(4).fillna(1)

    push_df['convert_second_rate'] = push_df['push_second'].div(
        push_df['push_second_fails'] + push_df['push_second']
    ).astype(float).round(4).fillna(1)

    # Fill nas
    for i in push_df.index:
        for j in push_df.columns:
            if pd.isna(push_df.loc[i,j]):
                push_df.loc[i,j] = 0
    push_df = push_df.reset_index().rename(columns={"index":"team"})

    # Number of rolls
    num_caps = round_events[round_events['type'] == 'pointcap'].groupby('round').size()

    num_caps = num_caps.reset_index().rename(columns={0:"num_caps"})

    num_caps = rounds_df.merge(num_caps)[['round','num_caps','winner']]

    rolls = num_caps[num_caps['num_caps'] ==3].groupby('winner').size().reset_index().rename(columns={'winner':"team",0:'rolls'})

    push_df = push_df.merge(rolls,how= 'left')

    # Avoid divide by zero
    push_df = push_df.replace(0,np.nan)
    push_df['roll_rate'] = (push_df['rolls'].div(len(rounds_df))).astype(float).round(4)

  ## LAST COMEBACKS ##
    # region Last comebacks
    # Groupby team and bind winner
    last_comebacks = push.copy().groupby('round').agg(
        points = ('point','sum')
    ).merge(rounds_df[['round','winner']], on='round', how='left')

    comebacks = pd.Series([0,0],index = ['Blue','Red'],name = "comebacks")

    # If winner's last is in round
    for i in range(0,len(last_comebacks)):
        team = last_comebacks.loc[i,'winner']
        s = f'{team}_Second'
        points_captured = last_comebacks.loc[i,'points']

        if s in points_captured:
            comebacks[team] += 1

    comebacks = comebacks.reset_index().rename(columns = {"index":"team"})

    push_df = push_df.merge(comebacks,how = 'left')

    push_df = push_df.replace(0,np.nan)

    # Merge in score to divide instead of being dumb
    team_score = teams_df[['score','team']].copy()

    push_df = push_df.merge(team_score,on = ['team'])
    
    push_df['comeback_rate'] = push_df['comebacks'].div(push_df['score']).astype(float).round(4)


    # endregion
    
    # endregion

    ## Lead changes ##
    # region Lead Changes

    push_df['lead_changes'] = push_df['push_mid'] + push_df['takeback_mid']
    # endregion

    # region number of caps
    pointcap = round_events[round_events['type'] == 'pointcap'].copy()

    group = pointcap.groupby(['team'])['point']

    group = group.value_counts().reset_index()

    group['point_rename'] = [point_names[point] for point in group['point']]

    group = group[['team','point_rename','count']]

    unstacked = group.set_index(['team','point_rename']).unstack('point_rename').reset_index()

    unstacked.columns = ['team'] + [col[1] for col in unstacked.columns if col[1] != ""]
    
    push_df = push_df.merge(unstacked,on = ['team'],how = 'left')
    
    # endregion
    
    return push_df

def team_medic_stats(players_df,medic_stats_df,teams_df):
    # Desired aggregation mapping
    agg_map = {
        "medicstats.advantages_lost": ("medicstats.advantages_lost", "sum"),
        "medicstats.avg_time_before_healing": ("medicstats.avg_time_before_healing", "mean"),
        "medicstats.avg_time_before_using": ("medicstats.avg_time_before_using", "mean"),
        "medicstats.avg_time_to_build": ("medicstats.avg_time_to_build", "mean"),
        "medicstats.avg_uber_length": ("medicstats.avg_uber_length", "mean"),
        "medicstats.biggest_advantage_lost": ("medicstats.biggest_advantage_lost", "max"),
        "medicstats.deaths_with_95_99_uber": ("medicstats.deaths_with_95_99_uber", "sum"),
        "medicstats.deaths_within_20s_after_uber": ("medicstats.deaths_within_20s_after_uber", "sum"),
        "ubers": ("ubers", "sum")
    }
    player_teams = players_df[['steamid','team']]

    # Merge and prepare the DataFrame
    merged_df = medic_stats_df.reset_index().merge(player_teams)

    # Filter agg_map to only include columns that actually exist
    existing_agg_map = {
        k: v for k, v in agg_map.items() if k in merged_df.columns
    }

    # Group and aggregate only the columns that exist
    team_medic_stats_df = merged_df.groupby('team').agg(**existing_agg_map)
    

    team_medic_stats_df = team_medic_stats_df.reset_index()
    team_medic_stats_df = team_medic_stats_df.merge((teams_df[['team','drops']]),how = 'left')

    cols_to_av = ['medicstats.deaths_with_95_99_uber','medicstats.deaths_within_20s_after_uber','drops']

    team_medic_stats_df = team_medic_stats_df.replace(0,np.nan)
    for col in cols_to_av:
        if col in team_medic_stats_df.columns:
            team_medic_stats_df[col + '_rate'] = team_medic_stats_df[col].div(team_medic_stats_df['ubers']).astype(float).round(4)
    
    return team_medic_stats_df
       