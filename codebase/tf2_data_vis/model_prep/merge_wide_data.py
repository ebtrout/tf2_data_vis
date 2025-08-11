import pandas as pd

def merge_wide_data(medic_wide,combat_wide,teams):
    medic_merger = medic_wide.drop(['id','team'],axis =1)

    # Merge medic and combat
    players_wide = pd.concat([combat_wide,medic_merger],axis = 1)

    players_wide = players_wide.merge(teams[['id','team','winner']],on =['id','team'])
    
    return players_wide
    # endregion