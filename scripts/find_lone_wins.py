"""Saves to file a table of players who have accomplished a lone win.

A lone win means that, given some restriction and a seed, the player's
team is the only team to win a game on that seed. A built-in requirement
is that all players on the team must not have played that seed previously.
By default, there must be at least 2 games satisfying the restriction on
the given seed, but this can be modified.
"""

import math
from bisect import bisect
from tqdm import tqdm
from hanabdata.process_games import get_players_with_x_games
from hanabdata.tools.structures import GamesIterator
from hanabdata.tools.io.read import write_csv, read_csv
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score

def make_table():
    """docstring"""
    co = [2, 5, 10, 50]
    temp = create_player_dict(*create_seed_dict())
    result = do_cutoff_stuff(temp, cutoffs=co)
    result2 = get_log_sum(temp)

    ans = [["Names"] + co + ["Log Sum", "Greatest Result", "Seed"]]
    for player, cols in result.items():
        newline = [player] + cols
        newline.append(result2[player])
        newline.extend(max(temp[player]))
        ans.append(newline)

    write_csv("data/processed/seeds/allwins.csv", ans)

    return ans

def create_seed_dict(restriction=get_standard_restrictions()):
    """docstring"""
    gi = GamesIterator()

    multiwin_seeds, seed_to_gc, seed_to_players, lonewins = set(), {}, {}, {}
    for game in tqdm(gi, total=1100000):
        seed = game["seed"]

        # not interested in seeds won by 2+ teams
        # if seed in multiwin_seeds:
        #     continue

        # save the identities of all players who have seen the deck.
        # not interested in games where a player has previously seen
        # the deck
        seed_to_players.setdefault(seed, set())
        players = game["playerNames"]
        good = True
        for player in players:
            if player in seed_to_players[seed]:
                good = False
            seed_to_players[seed].add(player)
        if not good:
            continue

        # not interested in games not satisfying the restriction
        if not restriction.validate(game):
            continue

        # interested in seeds won once but not twice
        if has_winning_score(game):
            # if seed in lonewins:
            #     del lonewins[seed]
            #     multiwin_seeds.add(seed)
            #     continue

            lonewins.setdefault(seed, set())
            lonewins[seed].update([(player, 1) for player in players])
        else:
            lonewins.setdefault(seed, set())
            lonewins[seed].update([(player, 0) for player in players])

        # counts all games played before 2nd win "under normal circumstances"
        seed_to_gc.setdefault(seed, [0, 0])
        seed_to_gc[seed][0] += 1
        if has_winning_score(game):
            seed_to_gc[seed][1] += 1

    return lonewins, seed_to_gc

def create_player_dict(seed_to_players, seed_to_gc):
    """docstring"""
    player_to_lonewins = {}
    for seed, players in tqdm(seed_to_players.items()):
        num_games, num_wins = seed_to_gc[seed]
        for (player, result) in players:
            player_to_lonewins[player] = player_to_lonewins.get(player, []) + [(num_games, num_wins, seed, result)]

    for lonewins in player_to_lonewins.values():
        lonewins.sort()

    return player_to_lonewins

def do_cutoff_stuff(player_to_lonewins, cutoffs=None):
    """docstring"""
    if cutoffs is None:
        cutoffs = [2]

    winners = {}
    for player, lonewins in tqdm(player_to_lonewins.items()):
        winners[player] = [0] * len(cutoffs)
        for (num_games, num_wins, _, result) in lonewins:
            if result == 0:
                continue
            for i, cutoff in enumerate(cutoffs):
                if cutoff > num_games / num_wins:
                    break
                winners[player][i] += 1

    return winners

def get_log_sum(player_to_lonewins):
    """Returns the log sum."""
    winners = {}
    for player, lonewins in tqdm(player_to_lonewins.items()):
        winners[player] = 0
        for (num_games, num_wins, _, result) in lonewins:
            if num_wins == 0:
                continue
            x = num_wins / num_games
            if result == 1:
                winners[player] += -math.log(x)
            else:
                if x == 1 or x == 1.0:
                    continue
                winners[player] += (x / (1 - x)) * math.log(x)

    return winners

if __name__ == "__main__":
    ans = make_table()

    print(ans[60])
    print(ans[155])
