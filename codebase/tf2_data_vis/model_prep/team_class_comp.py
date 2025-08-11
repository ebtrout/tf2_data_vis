import pandas as pd
# Test if there are 1 demo 2 scout 2 solider 1 med
def team_class_comp(players: pd.DataFrame):
        
    team_comp = players.groupby(['id', 'team'])['primary_class'].agg(lambda x: ".".join(x)).reset_index(name='class_concat')

    team_comps = (team_comp['class_concat'].str.split("."))

    # Test if team_comp is correct
    correct = []
    for team in team_comps:
        if len(team) != 6:
            correct.append(0)
            continue
        demoman = 0
        soldier = 0 
        scout = 0
        medic = 0
        for class_name in team:
            if class_name == 'demoman':
                demoman += 1
            if class_name == 'soldier':
                soldier += 1
            if class_name == 'scout':
                scout += 1
            if class_name == 'medic':
                medic += 1
        if demoman == 1 and soldier == 2 and scout == 2 and medic == 1:
            correct.append(1)
        else:
            correct.append(0)

    team_comp['correct'] = correct

    team_comp = team_comp.groupby('id').agg(correct_team_comp = ('correct','sum'))

    team_comp = team_comp[team_comp['correct_team_comp'] == 2]

    players_team_comp = players[players['id'].isin(team_comp.reset_index()['id'])].copy()

    return players_team_comp

