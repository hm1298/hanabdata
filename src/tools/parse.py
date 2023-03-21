from tools.gamestate import GameState as G
from tools import read


class UserData:
    """Class to extract specific info from user data so that 
    everything else can abstract away the structure of the data."""

    def __init__(self, data):
        self.data = data

    def get_ids(self):
        "Provides a list of game ids the user has played."
        return [game["id"] for game in self.data]

    def count(self):
        "Provides the number of games the user has played."
        return len(self.data)


class GameData:
    """Class to extract specific info from game data so that
    everything else can abstract away the structure of the data."""

    def __init__(self, data):
        self.data = data

    def get_players(self):
        "Provides the users who played the game."
        return self.data["players"]

    def get_player_count(self):
        "Provides the number of players in the game."
        return len(self.data["players"])

    def contains(self, player) -> bool:
        "Says whether a specific user played the game."
        return player in self.data["players"]

    def generate_summary(self):
        """Information is returned as ['# Turns Played', 'Score', '# Clue Tokens', '# Strikes']"""
        datalist = []
        for turn in range(1 + len(self.data["actions"])):
            game = G(self.data, turn)
            info = [game.turn, game.score,
                    game.clue_token_count, game.strike_count]
            datalist.append(info)
        return datalist

    def generate_line_summary(self):
        """Information provided about the game:
        [game_id, player_count, player_names, variant, 
            turn_count, score, strike_count, turns at 0 clues]
        """

        summary = self.generate_summary()

        # get string with player names
        player_names = self.data["players"][0]
        for name in self.data["players"][1:]:
            player_names = f'{player_names} {name}'

        # get variant
        variant = "No Variant"
        if 'options' in self.data:
            if 'variant' in self.data['options']:
                variant = self.data["options"]["variant"]

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
    for game_id in ids:
        print(f'generating summary for game {game_id}')
        datalist.append(GameData(read.read_game(
            game_id)).generate_line_summary())

    read.write_user_summary(username, datalist)

    print(len(datalist))


def get_seed_winrate(seed: str, restriction, winrate):
    print(f'getting winrate for seed {seed}')
    win_count, eligible = 0, 0
    data = read.read_seed(seed)
    for game in data:
        if restriction.validate(game):
            eligible += 1
            if winrate.validate(game):
                win_count += 1

    winrate = win_count / eligible
    return winrate


def generate_winrate_summary(seeds, restriction, winrate):
    winrates = [['seed', 'winrate']]
    for seed in seeds:
        try:
            w = get_seed_winrate(seed, restriction, winrate)
        except:
            print("error")
            w = 'N/A'
        winrates.append([seed, w])

    read.write_winrate_seeds(0, winrates)


# no longer used anywhere? this method and get_noncheating_options()
# may now be safely folded into restrictions.py, not sure
def verify_no_cheating(game):
    """
    Redundant code. Returns True if no cheating occured in game.
    May be better to move other uses here or to move this elsewhere, idk
    """
    for key in NONCHEATING_OPTIONS:
        if game["options"][key] != NONCHEATING_OPTIONS[key]:
            return False
    return True


def get_option_keys():
    return [
        "numPlayers",
        "startingPlayer",
        "variantID",
        "variantName",
        "timed",
        "timeBase",
        "timePerTurn",
        "speedrun",
        "cardCycle",
        "deckPlays",
        "emptyClues",
        "oneExtraCard",
        "oneLessCard",
        "allOrNothing",
        "detrimentalCharacters",
    ]


def get_noncheating_options():
    return {
        "startingPlayer": 0,
        "cardCycle": False,
        "deckPlays": False,
        "emptyClues": False,
        "oneExtraCard": False,
        "oneLessCard": False,
        "allOrNothing": False,
        "detrimentalCharacters": False,
    }


NONCHEATING_OPTIONS = get_noncheating_options()
