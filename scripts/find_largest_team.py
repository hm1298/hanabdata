"""This script finds the game and team with largest "Games Played" according to Hanab Live's GetUserGames: https://github.com/Hanabi-Live/hanabi-live/blob/c936808df2b78aa4a24be7b0d622fceb75393f17/server/src/models_games.go#L670."""

import heapq as h
from hanabdata.tools.structures import  GamesIterator
from hanabdata.tools.io.read import write_csv
from hanabdata.tools.restriction import Restriction

def find_largest_team(top_x):
    """Script."""
    gi = GamesIterator()
    only_good_games = {"options":{"speedrun":False},"endCondition":1}
    res = Restriction(only_good_games, {})

    games = []
    player_to_games_played = {}

    counter = 0
    for game in gi:
        if not res.validate(game):
            continue

        rating = 0
        for player in game["playerNames"]:
            player_to_games_played[player] = player_to_games_played.get(player, 0) + 1
            rating += player_to_games_played[player]

        game_id = game["id"]

        # games.append((rating, game_id))
        h.heappush(games, (rating, game_id))
        if len(games) > top_x:
            h.heappop(games)
        # counter += 1
        # if counter > 100000:
        #     break

    return sorted(games)[-top_x:]

if __name__ == "__main__":
    info = find_largest_team(100)
    print(info)
    table = [["Combined Games Played", "Game ID"]]
    file_path = './data/largest_teams.csv'
    for user, num_games in info:
        table.append([user, num_games])
    write_csv(file_path, table)
