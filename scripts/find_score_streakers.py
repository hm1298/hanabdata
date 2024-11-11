"""This script looks through a given variant to determine which players have the longest streak of successive wins (maximum score)."""

from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score
from hanabdata.tools.io.read import write_csv
from hanabdata.tools.structures import  GamesIterator
from hanabdata.game.variants import get_variant_names_dict

def score_streak_analysis(variants=None):
    """_summary_"""
    gi = GamesIterator()
    res = get_standard_restrictions()
    del(res.necessary_constraints["numTurns"])

    streaks = {}

    for game in gi:
        if not res.validate(game):
            continue
        # if game["options"]["numPlayers"] != 2:
        #     continue
        curr_variant = game["options"]["variantName"]
        if not variants:
            curr_variant = "All Variants"
        elif curr_variant not in variants:
            continue

        for player in game["playerNames"]:
            if curr_variant not in streaks:
                streaks[curr_variant] = {}
            if player not in streaks[curr_variant]:
                streaks[curr_variant][player] = [0, 0]

            if not has_winning_score(game):
                streaks[curr_variant][player][0] = 0
            else:
                streaks[curr_variant][player][0] += 1
                streaks[curr_variant][player][1] = max(streaks[curr_variant][player][0], streaks[curr_variant][player][1])

    return streaks


if __name__ == "__main__":
    all_variants = list(get_variant_names_dict().keys())
    var_to_results = score_streak_analysis(all_variants)
    info = var_to_results["No Variant"]
    print("got data")

    count = 0
    good_vars = []
    for variant, data in var_to_results.items():
        if max(data.values(), key=lambda tup: tup[1])[1] > 6:
            count += 1
            good_vars.append(variant)
    print(count, "good variants")
    print(*good_vars, sep="\n")

    table = [["No Variant", "Current Streak", "Longest Streak"]]
    file_path = './data/processed/score_streaks/no_variant.csv'
    for user, num_games in info.items():
        table.append([user, num_games[0], num_games[1]])
    write_csv(file_path, table)
