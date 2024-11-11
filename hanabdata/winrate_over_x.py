"""~
"""

from tqdm import tqdm
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score
from hanabdata.tools.structures import GamesIterator

def find_winrate(players, sample_size, variant="No Variant"):
    """~"""
    restriction = get_standard_restrictions(2)
    del restriction.necessary_constraints["numTurns"]

    gi = GamesIterator()
    games = []
    for game in tqdm(gi, total=1100000):
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

if __name__ == '__main__':
    players = ["GCaly"]
    find_winrate(players, 100)
