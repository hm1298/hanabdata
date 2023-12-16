"""This script looks through a given variant to determine which players have the longest streak of successive wins (maximum score)."""

import datetime
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score
from hanabdata.tools.io.read import write_csv
from hanabdata.tools.structures import  GamesIterator

def find_longest_game(variants=None):
    """_summary_"""
    gi = GamesIterator()
    res = get_standard_restrictions()
    del(res.necessary_constraints["numTurns"])

    games = []
    streaks = {}

    for game in gi:
        if not res.validate(game):
            continue
        if game["options"]["numPlayers"] != 3:
            continue
        curr_variant = game["options"]["variantName"]
        if not variants:
            curr_variant = "All Variants"
        elif curr_variant not in variants:
            continue

        game_id = game["id"]

        start_time = datetime.datetime.fromisoformat(game['datetimeStarted'])
        end_time = datetime.datetime.fromisoformat(game['datetimeFinished'])
        game_dur = (end_time - start_time).total_seconds()

        games.append((game_dur, game_id))

    print("done")

    return sorted(games)[-10:]


if __name__ == "__main__":
    info = find_longest_game(["No Variant"])
    print(info)
