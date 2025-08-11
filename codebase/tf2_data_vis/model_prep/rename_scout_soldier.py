import random
import numpy as np

def rename_scout_soldier(players_subset):
    # Copy the DataFrame so we don't overwrite the original
    players_fixed_class_names = players_subset.copy()

    # Group by match id and team
    grouped = players_fixed_class_names.groupby(['id', 'team'])

    # Apply function to each group
    players_fixed_class_names = grouped.apply(rename_classes_randomly, include_groups=False).reset_index()

    # Drop the redundant index column
    if 'level_2' in players_fixed_class_names.columns:
        players_fixed_class_names.drop('level_2', axis=1, inplace=True)
    return players_fixed_class_names

# Function to randomly rename duplicate classes within each group
def rename_classes_randomly(df):
    random.seed(123)
    np.random.seed(123)
    df = df.copy()  # avoid SettingWithCopyWarning
    for cls in ['scout', 'soldier']:
        indices = df.index[df['primary_class'] == cls].tolist()
        if len(indices) == 2:
            # Randomly shuffle the suffixes
            suffixes = [f"{cls}_1", f"{cls}_2"]
            random.shuffle(suffixes)
            for i, idx in enumerate(indices):
                df.at[idx, 'primary_class'] = suffixes[i]
    return df