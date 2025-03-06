"""~
"""

import datetime
import heapq
import pandas as pd
from tqdm import tqdm
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score
from hanabdata.tools.structures import GamesIterator, FullGamesIterator

def find_winrate(players, sample_size, variant="No Variant"):
    """~"""
    restriction = get_standard_restrictions(2)
    del restriction.necessary_constraints["numTurns"]

    gi = GamesIterator()
    games = []
    for game in tqdm(gi, total=1300000):
        satisfies = set(players).issubset(game["playerNames"])
        if not satisfies:
            continue
        if variant != game["options"]["variantName"]:
            continue
        if not restriction.validate(game):
            continue

        info = (game["id"], has_winning_score(game))
        games.append(info)

    sample = games[len(games) - sample_size:]
    count, total = 0, 0
    for game in sample:
        total += 1
        if game[1]:
            count += 1

    print(players, total, count, count / total)

def find_shortest_wins(sample_size, variant="No Variant"):
    """..."""
    gi = GamesIterator()
    games = []
    for game in tqdm(gi, total=1300000):
        if game["options"]["variantName"] != variant:
            continue
        if game["options"]["numPlayers"] != 2:
            continue
        if not has_winning_score(game):
            continue

        start_time = datetime.datetime.fromisoformat(game['datetimeStarted'])
        end_time = datetime.datetime.fromisoformat(game['datetimeFinished'])
        duration = (end_time - start_time).total_seconds()

        info = (game["numTurns"], game["id"], *game["playerNames"], duration)
        games.append(info)

    sample = heapq.nsmallest(sample_size, games)
    df = pd.DataFrame(sample, columns=["Number of Turns", "Game ID", "Alice", "Bob", "Duration (seconds)"])

    print(*sample, sep="\n")
    print(df)

if __name__ == '__main__':
    # players = ["hallmark"]
    # find_winrate(players, 100)
    find_shortest_wins(60)
