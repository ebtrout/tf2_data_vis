import pandas as pd
def make_X_y(players_wide):
        
    drop_cols = ['team','winner'] + [col for col in players_wide.columns if 'steamid' in col]

    X = players_wide.drop(drop_cols,axis = 1).copy()

    y = players_wide['winner']

    # Rank the scout and soldier data based on the entire dataset, not the pivot version
    scout_soldier = X[[col for col in X.columns if 'scout' in col or 'soldier' in col or 'id' in col]].copy()

    # Turn the data into long by binding together scout and soldier1 and 2 to compare against
    scout_soldier_long = pd.DataFrame()
    for index in ['1','2']:
        df = scout_soldier[[col for col in scout_soldier.columns if index in col]].copy()
        df.columns = [col.replace("_"+index,"") for col in df.columns]
        df['num']= index
        scout_soldier_long = pd.concat([scout_soldier_long,df])

    # Drop index and rank and reattach 1 or 2
    num = scout_soldier_long['num']
    scout_soldier_long.drop("num",axis =1,inplace = True)
    ranked_scout_soldier = scout_soldier_long.rank(pct=True)
    # Re attach index
    ranked_scout_soldier['num'] = num

    # Widen the datset again
    scout_soldier_ranked = pd.DataFrame()
    for index in ['1','2']:
        df = ranked_scout_soldier[ranked_scout_soldier['num'] == index].copy()
        df.drop('num',axis = 1,inplace = True)
        df.columns = [col + "_" + index for col in df.columns]
        scout_soldier_ranked = pd.concat([scout_soldier_ranked,df],axis = 1)

    # Add id back in
    scout_soldier_ranked['id'] = scout_soldier['id']


    # Rank the medic and demo stats
    medic_demo = X[[col for col in X.columns if 'scout' not in col and 'soldier' not in col and 'id' not in col]].copy()

    # Rank all other columns (percentage ranks)
    medic_demo_ranked = medic_demo.rank(pct=True)

    # Merge data back together

    X = pd.concat([scout_soldier_ranked,medic_demo_ranked],axis = 1)

    return X,y