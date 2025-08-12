import pandas as pd
import os
import numpy as np
def fix_push_stats(parent_dir,output_dir):
    path = os.path.join(parent_dir,'..',output_dir,'push_stats.csv')
    push_stats = pd.read_csv(path)

    path = os.path.join(parent_dir,'..',output_dir,'koth_rounds.csv')
    koth_rounds = pd.read_csv(path)

    koth_ids = koth_rounds['id'].unique()

    koth_push_stats = push_stats[push_stats['id'].isin(koth_ids)]

    push_stats = push_stats[~push_stats['id'].isin(koth_ids)]

    nan_cols = [col for col in koth_push_stats.columns if col != "id" and col != "team"]

    for col in nan_cols:
        koth_push_stats[col] = koth_push_stats[col].astype(float)
        koth_push_stats[col] = np.nan

        # Get unique IDs as a DataFrame
    append_nan = pd.DataFrame({'id': push_stats['id'].unique()})

    # Reindex to have same columns as koth_stats
    append_nan = append_nan.reindex(columns=koth_rounds.columns)

    # Concatenate
    koth_rounds_nan = pd.concat([koth_rounds, append_nan], ignore_index=True)



    push_stats = pd.concat([push_stats,koth_push_stats])

    path = os.path.join(parent_dir,'..',output_dir,'test_push_stats.csv')
    push_stats.to_csv(path,index = False)

    koth_rounds_nan = pd.concat([koth_rounds,append_nan])
    path = os.path.join(parent_dir,'..',output_dir,'koth_rounds.csv')
    koth_rounds_nan.to_csv(path,index = False)
    

