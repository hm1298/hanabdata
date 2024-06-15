"""File to fold into process_games.py for use by all scripts."""

import math
import numpy as np
import pandas as pd
from tqdm import tqdm
from hanabdata.tools.structures import GamesIterator
from hanabdata.tools.io.read import write_csv, read_csv
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score

BLOCKED_PLAYERS = {"Carunty", "FrancisFok", "yagami_blank", "yagami_blue", "yagami_light", "yagami_green", "yagami_red", "yagami_white"}
HIDDEN_PLAYERS = ["hallmark"]

def analyze():
    """docstring"""
    restriction = get_standard_restrictions()
    filename = "data/seed_table.csv"

    tup = process_for_seeds(restriction)
    data = make_table(tup)

    write_csv(filename, data)

def make_table(dicts):
    """docstring"""
    seed_to_gc, seed_to_players, lonewins = dicts

    table = [["Seed", "Variant Name", "Total # Legal Games", "Total # Legal Wins", "Total # Legal Losses"]]

    for seed, gc in seed_to_gc.items():
        variant = f"{gc[2]} {gc[3]}p"
        table.append([seed, variant, gc[0], gc[1], gc[0] - gc[1]])
    return table

def process_for_seeds(restriction):
    """docstring"""
    gi = GamesIterator()

    seed_to_gc, seed_to_players, lonewins = {}, {}, {}
    for game in tqdm(gi, total=1100000):
        seed = game["seed"]

        # save the identities of all players who have seen the deck.
        # not interested in games where a player has previously seen
        # the deck or is otherwise blocked from my metrics
        seed_to_players.setdefault(seed, set())
        players = game["playerNames"]
        good = True
        for player in players:
            if player in seed_to_players[seed] or player in BLOCKED_PLAYERS:
                good = False
            seed_to_players[seed].add(player)
        if not good:
            continue

        # not interested in games not satisfying the restriction
        if not restriction.validate(game):
            continue

        # interested in seeds won once or more
        if has_winning_score(game):
            lonewins.setdefault(seed, set())
            lonewins[seed].update([(player, 1) for player in players])
        else:
            lonewins.setdefault(seed, set())
            lonewins[seed].update([(player, 0) for player in players])

        # counts all games played "under normal circumstances"
        seed_to_gc.setdefault(seed, [0, 0, game["options"]["variantName"], game["options"]["numPlayers"]])
        seed_to_gc[seed][0] += 1
        if has_winning_score(game):
            seed_to_gc[seed][1] += 1

    return seed_to_gc, seed_to_players, lonewins

def analyze_players():
    """docstring"""
    restriction = get_standard_restrictions()
    filename = "data/player_metrics.csv"

    tup = process_for_players(restriction)
    data = make_metrics(tup)

    data.to_csv(filename)

def make_dict():
    """docstring"""
    filename = "data/seed_table.csv"

    rows = iter(read_csv(filename))
    next(rows)

    seed_to_nums = {}
    for (seed, _, *args) in rows:
        total, wins, losses = [int(x) for x in args]
        seed_to_nums[seed] = [wins / total, losses / total]

    return seed_to_nums

def make_metrics(metrics):
    """"docstring"""
    columns = ["Total Wins", "HM Wins", "GM Wins", "AM Wins", "RMS Wins", "Total Losses", "HM Losses", "GM Losses", "AM Losses", "RM Losses", "Total Games"]

    normalized_metrics = {}
    for player, stats in metrics.items():
        wins, losses = stats[0][0], stats[1][0]

        # fix? can include gamers who never lose, lol..
        if wins == 0:
            result = [0] * 5
        else:
            result = [wins] + [x / wins for x in stats[0][1:]]
            result[1] = 1 / result[1]
            result[2] = math.exp(result[2])
            result[4] = math.sqrt(result[4])
        if losses == 0:
            result += [0] * 5
        else:
            result += [losses] + [x / losses for x in stats[1][1:]]
            result[6] = 1 / result[6] if result[6] != 0 else np.nan
            result[7] = math.exp(result[7])
            result[9] = math.sqrt(result[9])
        result.append(result[0] + result[5])
        if result[10] < 100:
            continue
        normalized_metrics[player] = result

    df = pd.DataFrame.from_dict(normalized_metrics, orient='index', columns=columns)
    return df

def process_for_players(restriction, to_update=False):
    """docstring"""
    if to_update:
        analyze()
    seed_to_difficulty = make_dict()
    gi = GamesIterator()

    seed_to_players, player_to_metrics = {}, {}
    for game in tqdm(gi, total=1100000):
        seed = game["seed"]

        # save the identities of all players who have seen the deck.
        # not interested in games where a player has previously seen
        # the deck or is otherwise blocked from my metrics
        seed_to_players.setdefault(seed, set())
        players = game["playerNames"]
        good = True
        for player in players:
            if player in seed_to_players[seed] or player in BLOCKED_PLAYERS:
                good = False
            seed_to_players[seed].add(player)
        if not good:
            continue

        # not interested in games not satisfying the restriction
        if not restriction.validate(game):
            continue

        # initializes any new players
        for player in players:
            if player not in player_to_metrics:
                player_to_metrics[player] = [[0] * 5, [0] * 5]

        # updates players' metrics
        won = 0 if has_winning_score(game) else 1
        for player in players:
            player_to_metrics[player][won][0] += 1

            diff = 1 / seed_to_difficulty[seed][won]
            # HM
            player_to_metrics[player][won][1] += 1 / diff
            # GM
            player_to_metrics[player][won][2] += math.log(diff)
            # AM
            player_to_metrics[player][won][3] += diff
            # RMS
            player_to_metrics[player][won][4] += diff ** 2

    return player_to_metrics

if __name__ == "__main__":
    analyze()
    analyze_players()
