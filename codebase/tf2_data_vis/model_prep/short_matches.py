def short_matches(info,player_team_comp,short_match_cutoff = 450):
    info_team_comp = info[info['id'].isin(player_team_comp['id'].values)]

    short_matches = info_team_comp[info_team_comp['length'] < short_match_cutoff]
    players_subset = player_team_comp[~player_team_comp['id'].isin(short_matches['id'])].copy()
    return players_subset
