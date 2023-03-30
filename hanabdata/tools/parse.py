"""This module contains tools to take raw JSON data and 
process it into something more useful to us mortals"""

from hanabdata.game.gamestate import GameState as G
from .io import read


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
    """Provides an overview of a user's data from their summary JSON"""
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


def get_seed_success_rate(seed, restriction, goal):
    """Provides the success rate of goal in a given seed JSON, filtering
    out any games not meeting a given restriction.
    """
    print(f'getting winrate for seed {seed}')

    win_count, eligible = 0, 0
    data = read.read_seed(seed)
    for game in data:
        if restriction.validate(game):
            eligible += 1
            if goal.validate(game):
                win_count += 1

    if eligible == 0:
        return 'N/A'
    rate = win_count / eligible
    return rate


def generate_success_rate_summary(seeds, restriction, goal):
    """Provides a table of success rates for a list of seeds."""
    winrates = [['seed', 'winrate']]
    for seed in seeds:
        rate = get_seed_success_rate(seed, restriction, goal)
        winrates.append([seed, rate])

    read.write_winrate_seeds(0, winrates)
