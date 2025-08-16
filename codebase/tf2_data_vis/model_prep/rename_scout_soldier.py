import random
import numpy as np
import pandas as pd

def rename_scout_soldier(players_subset):
    players_fixed_class_names = players_subset.copy()
    players_scout_soldier = players_fixed_class_names[players_fixed_class_names['primary_class'].isin(['scout','soldier'])]
    players_medic_demo = players_fixed_class_names[~players_fixed_class_names['primary_class'].isin(['scout','soldier'])]
    df = players_scout_soldier.copy()

    # Step 1 — Find max hr_pct in each group
    group_cols = ['id', 'team', 'primary_class']
    df['max_hr_pct'] = df.groupby(group_cols)['hr_pct'].transform('max')
    df['min_hr_pct'] = df.groupby(group_cols)['hr_pct'].transform('min')

    # Find a classroll
    df['role'] = np.where( np.abs(df['hr_pct'] - df['max_hr_pct']) <= .0001,'pocket','roamer')

    # If multiple roles exist assign them randomly
    df['role_check'] = df.groupby(group_cols)['role'].transform('sum')

    df_bad = df[df['role_check'].isin(['roamerroamer','pocketpocket'])].copy()

    # Apply Function to randomly assign one 'pocket' and one 'roamer' per group
    df_bad = df_bad.groupby(['id','team','primary_class'], group_keys=False).apply(assign_roles_randomly,include_groups = False)

    # Put the results back into the original DataFrame
    df.update(df_bad)
    df['primary_class'] = df['primary_class'] + "_" + df['role']
    df.drop(['role','role_check'],axis = 1,inplace = True)

    # Concat
    players_scout_soldier = df
    players_fixed_class_names = pd.concat([players_medic_demo,players_scout_soldier])

    return players_fixed_class_names

# Function to randomly rename duplicate classes within each group
def assign_roles_randomly(group):
        idx = group.sample(2, random_state=np.random.randint(0, 1_000_000)).index
        group.loc[idx[0], 'role'] = 'pocket'
        group.loc[idx[1], 'role'] = 'roamer'
        return group