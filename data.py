import create_datasets as cd

class data:
    def __init__(self,log,id):
        ## Init
        self.log = log
        self.id = id

        self.info = self.create_info()
        self.players = self.create_players()
        
        # Create medic stats and drop them from players
        self.players, self.medic_stats = self.create_medic_stats()

        # Create class stats and drop them from players
        self.players, self.medic_stats = self.create_class_stats()

        self.teams = self.create_teams()
        self.class_av = None
        self.class_stats = None
        self.team_stats = None
        self.class_kda = None
        self.class_kda_per_class = None
        self.team_medic_stats = None
        self.push_stats = None
        self.healspread = None
        self.rounds = None
        self.round_events = None
    
    def create_info(self):
        info = cd.info(log = self.log,id = self.id)
        return info
    
    def create_players(self):
        players = cd.players(log = self.log)
        return players
    
    def create_medic_stats(self):
        players, medic_stats = cd.medic_stats(self.players)
        return players,medic_stats
    
    def create_class_stats(self):
        players, class_stats = cd.class_stats(self.players)
        return players, class_stats
    
    def create_teams(self):
        teams = cd.teams(self.log)
        return(teams)


    