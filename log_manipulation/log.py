import create_datasets as cd
import player_cols 
import team_cols
import advanced_med_stats

# Organized class that takes in a logs.tf log and turns it into
# A log class that contains all useful data from it 

class log:
    def __init__(self,log,id):
        ## Init From Log
        self.log = log
        self.id = id

        ## INITIALIZE DATASETS ## 
        self.info = self.create_info()
        self.players = self.create_players()
        self.teams = self.create_teams()
        self.rounds = self.create_rounds()
        self.player_rounds = self.create_player_rounds()
        self.class_kda = self.create_class_kda()
        
        
        # Create medic stats and drop them from players
        self.players, self.medic_stats = self.create_medic_stats()

        # Create class stats and drop them from players
        self.players, self.class_stats = self.create_class_stats()

        # Create round_events and drop them from rounds
        self.rounds, self.round_events = self.create_round_events()

        # Create push_stats REQUIRES ROUND EVENTS
        self.push_stats = self.create_push_stats()

        # Create team_medic_stats REQUIRES MEDIC_STATS PLAYERS
        self.team_medic_stats = self.create_team_medic_stats()
        
        # Add More Advanced Columns
        self.teams = self.add_team_cols()
        self.players = self.add_player_cols()

        # Create Healspread REQUIRES add_player_cols()
        self.healspread = self.create_healspread()

        # Add advanced medic stats REQUIRES team_medic_stats,players,round events
        self.advanced_med_stats_params()
        self.team_medic_stats = self.add_advanced_med_stats()
        
    def advanced_med_stats_params(self):
        self.exchange_width = 6

        self.success_width = 30

        self.medic_death_width = 15

        self.drops_forced_width = 15

        self.medic_death_capitalize_window = 25

        self.round_losing_medic_death_window = 12

    
    def create_info(self):
        info = cd.info(log = self.log,id = self.id)
        return info
    
    def create_players(self):
        players = cd.players(log = self.log)
        return players
    
    def create_medic_stats(self):
        players, medic_stats = cd.medic_stats(players = self.players)
        return players,medic_stats
    
    def create_class_stats(self):
        players, class_stats = cd.class_stats(players = self.players)
        return players, class_stats
    
    def create_teams(self):
        teams = cd.teams(log = self.log)
        return teams
    
    def create_rounds(self):
        rounds = cd.rounds(log = self.log)
        return rounds
    
    def create_round_events(self):
        rounds, round_events = cd.round_events(rounds = self.rounds)
        return rounds, round_events

    def create_player_rounds(self):
        player_rounds = cd.player_rounds(log = self.log)
        return player_rounds
    
    def create_healspread(self):
        healspread = cd.healspread(log = self.log,players = self.players)
        return healspread
    
    def create_class_kda(self):
        class_kda = cd.class_kda(log = self.log)
        return class_kda
    
    def create_push_stats(self):
        push_stats = cd.push_statistics(round_events = self.round_events,rounds_df = self.rounds,teams_df = self.teams)
        return push_stats
    
    def create_team_medic_stats(self):
        team_medic_stats = cd.team_medic_stats(players_df = self.players,medic_stats_df=self.medic_stats,teams_df=self.teams)
        return team_medic_stats
    
    def add_team_cols(self):
        teams = self.teams
        players = self.players

        teams = team_cols.midfight_conversion(rounds = self.rounds,teams = teams)

        teams = team_cols.counting_stats(players = players,teams = teams)

        teams = team_cols.round_length(teams = teams, rounds = self.rounds)
        
        teams = team_cols.winner(teams = teams)

        return teams

    def add_player_cols(self):
        players = self.players
        class_stats = self.class_stats
        teams = self.teams

        players = player_cols.names(log = self.log, players = players)

        players = player_cols.primary_class(class_stats=class_stats,players = players)

        players = player_cols.offclass(class_stats = class_stats,players = players)

        players = player_cols.player_percentages(teams = teams,players = players)

        players = player_cols.hroi(players = players)

        players = player_cols.healps(players = players)

        players = player_cols.suicide_rate(players = players)

        return players
    

    def add_advanced_med_stats(self):
        exchange_width = self.exchange_width
        success_width = self.success_width
        medic_death_width = self.medic_death_width
        drops_forced_width = self.drops_forced_width
        medic_death_capitalize_window = self.medic_death_capitalize_window
        round_losing_medic_death_window = self.round_losing_medic_death_window
        players = self.players
        round_events = self.round_events
        rounds = self.rounds
        team_medic_stats = self.team_medic_stats

        team_medic_stats = advanced_med_stats.post_uber(
            exchange_width=exchange_width,
            success_width=success_width,
            medic_death_width=medic_death_width,
            drops_forced_width=drops_forced_width,
            medic_death_capitalize_window=medic_death_capitalize_window,
            round_losing_medic_death_window=round_losing_medic_death_window,
            players=players,
            round_events=round_events,
            team_medic_stats=team_medic_stats
        )

        team_medic_stats = advanced_med_stats.additional_rates(rounds = rounds,players = players,
                                                               team_medic_stats=team_medic_stats)
        
        return team_medic_stats



