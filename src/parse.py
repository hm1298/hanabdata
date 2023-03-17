
from gamestate import GameState as G
import read

class UserData:

    
    def __init__(self, data):
        self.data = data
    
    def get_ids(self):
        return [game["id"] for game in self.data]
    
    def count(self):
        return len(self.data)
    

class GameData:
    def __init__(self, data):
        self.data = data
    
    def get_players(self):
        return self.data["players"]
    
    def get_player_count(self):
        return len(self.data["players"])
    
    def contains(self, player):
        if player in self.data["players"]:
            return True
        return False

    def generate_summary(self):
        information = ['Turns Played', 'Score', 'Clue Tokens', 'Strikes']
        datalist = []
        for turn in range(1 + len(self.data["actions"])):
            game = G(self.data, turn)
            info = [game.turn, game.score, game.clue_token_count, game.strike_count]
            datalist.append(info)
        return datalist

    def generate_line_summary(self):
        
        
        summary = self.generate_summary()

        # get string with player names
        player_names = self.data["players"][0]
        for name in self.data["players"][1:]:
            player_names = f'{player_names} {name}'

        # get variant
        try: 
            variant = self.data["options"]["variant"]
        except:
            variant = "No Variant"

        # get turn count
        turn_count = len(self.data["actions"])

        # get score
        score = summary[-1][1]

        # get strike count
        strike_count = summary[-1][3]

        # count turns at 0 clues
        turns_at_0_clues = 0
        for row in summary:
            if row[2] < 1:
                turns_at_0_clues += 1
        
        
        line_summary = [
            self.data["id"], 
            len(self.data["players"]), 
            player_names, 
            variant,
            turn_count, 
            score, 
            strike_count,
            turns_at_0_clues,
        ]

        return line_summary






def generate_user_summary(username: str):
    ids = read.read_game_ids(username)
    information = [
            'ID', 
            'Player Count', 
            'Player Names', 
            'Variant', 
            'Turn Count', 
            'Score', 
            'Strike Count', 
            'Turns at 0 clues'
    ]
    datalist = [information]
    for id in ids: 
        print(f'generating summary for game {id}')
        datalist.append(GameData(read.read_game(id)).generate_line_summary())

    read.write_user_summary(username, datalist)

    print(len(datalist))

def get_seed_winrate(seed: str):
    print(f'getting winrate for seed {seed}')
    win_count = 0
    data = read.read_seed(seed)
    for game in data:
        if game["score"] == 25:
            win_count += 1

    winrate = win_count / len(data)
    return winrate

def generate_winrate_summary():
    winrates = [['seed', 'winrate']]
    for i in range(100):
        seed = f'p2v0s{i + 1}'
        try:
            w = get_seed_winrate(seed)
        except:
            w = 'N/A'
        winrates.append([seed, w])

    read.write_winrate_seeds(0, winrates)
    