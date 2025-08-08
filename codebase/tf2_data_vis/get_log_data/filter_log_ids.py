import pandas as pd
import re
import string
import pandas as pd
from collections import Counter


def filter_log_ids(log_ids,map_cutoff = 100,request_params = {}):
    cutoff_date = request_params['cutoff_date']
    log_ids = log_ids.drop_duplicates()
    log_ids = log_ids.dropna()

    correct_titles = title_includes(str_list = ['ugc', 'etf2l', 'rgl', 'scrim', 'lan','invite'],
                                    log_ids = log_ids)
    remove_pl_pass_df = remove_pl_pass(correct_titles= correct_titles)

    map_names = get_map_names(remove_pl_pass_df= remove_pl_pass_df,
                               map_cutoff= 100)
                               
    correct_date = date_beyond(remove_pl_pass_df = remove_pl_pass_df, cutoff_date = cutoff_date)

    filtered_log_ids = map_includes(correct_date=correct_date,
                                map_names = map_names)
    
    return filtered_log_ids

def title_includes(str_list : list[str],
                   log_ids : pd.DataFrame):
    include_pattern = r'\b(?:' + '|'.join(re.escape(s) for s in str_list) + r')\b'
    exclude_pattern = r'\bpug\b'

    # Preprocess the 'title' column
    log_ids['title_clean'] = (
        log_ids['title']
        .str.lower()
        .str.translate(str.maketrans('', '', string.punctuation))
    )

    # Apply both include and exclude filters
    correct_titles = log_ids[
        log_ids['title_clean'].str.contains(include_pattern, regex=True, na=False) &
        ~log_ids['title_clean'].str.contains(exclude_pattern, regex=True, na=False)
    ]
    return correct_titles

def remove_pl_pass(correct_titles):
    remove_pl_pass_df = correct_titles[~correct_titles['map'].str.lower().str.startswith('pl_')]
    remove_pl_pass_df = remove_pl_pass_df.reset_index(drop = True)
    remove_pl_pass_df = remove_pl_pass_df[~remove_pl_pass_df['map'].str.lower().str.startswith('pass_')]
    return remove_pl_pass_df

def get_map_names(remove_pl_pass_df,map_cutoff = 100):
    
    # Count the number of map occurances
    token_counts = Counter()

    for row in remove_pl_pass_df["map"]:
        tokens = str(row).lower().split("_")
        token_counts.update(tokens)

    map_counts = pd.DataFrame(token_counts.items(), columns=["token", "count"])
    map_counts = map_counts.sort_values(by="count", ascending=False)
    
    # Remove junk tokens
    map_counts = map_counts[map_counts['token'].str.len() > 3]
    map_counts = map_counts[map_counts['token'].str.split(" ").str.len() <= 1]
    map_counts = map_counts[map_counts['token'].str.fullmatch(r'[a-zA-Z]+')]
    map_counts = map_counts[~map_counts['token'].str.contains('final')]
    map_counts = map_counts[~map_counts['token'].str.contains('koth')]
    map_counts = map_counts[~map_counts['token'].str.contains('cp')]

    # Only look at map names > map_cutoff
    map_names = map_counts[map_counts['count'] > map_cutoff]['token']
    
    return map_names

def map_count(s,map_names):
    count = 0
    for map_name in map_names:
        if map_name in s:
            count +=1
    return count

def map_includes(correct_date, map_names):
    correct_date['map_count'] = correct_date['map'].apply(map_count,map_names = map_names)
    correct_maps = correct_date[correct_date['map_count'] == 1]
    return correct_maps

def date_beyond(remove_pl_pass_df,cutoff_date):
    correct_date = remove_pl_pass_df[remove_pl_pass_df['date'] > cutoff_date]
    return correct_date
