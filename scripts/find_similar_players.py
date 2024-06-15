"""
This script finds players who take similar actions in identical
gamestates.
"""

import json
from tqdm import tqdm
from hanabdata.tools import structures
from hanabdata.tools.io.read import write_csv, read_csv
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score

BLOCKED_PLAYERS = {}
HIDDEN_PLAYERS = ["hallmark"]

def main():
    """script execution"""
    # go through all games and create a dictionary of seed names to list of data
    # sort each list by game actions
    res = get_standard_restrictions()
    del res.necessary_constraints["numTurns"]
    seed_to_games, _ = process_for_seeds(get_standard_restrictions(), 10)
    print(seed_to_games)
    # go through all seeds and create a double dictionary of players to players to count
    # count the total number of games played, the number of matching gamestates, the number of matching gamestates with similar action chosen (clue<->clue, play<->play), the number of matching gamestates with identical action chosen, the number of matching gamestates with any clue chosen, and the number of matching gamestates with identical clue chosen

    print("done")

def process_for_seeds(restriction, stop_short=9**9):
    """docstring"""
    gi = structures.FullGamesIterator()

    seed_to_games, seed_to_deck, seed_to_players = {}, {}, {}
    count = 0
    for game in tqdm(gi, total=1100000):
        seed = game["seed"]
        seed_to_deck.setdefault(seed, game["deck"])

        # save the identities of all players who have seen the deck.
        # not interested in games where a player has previously seen
        # the deck or is otherwise blocked from my metrics
        seed_to_players.setdefault(seed, set())
        players = game["players"]
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

        # stores all games (limited to actions & players) played "under
        # normal circumstances"
        seed_to_games.setdefault(seed, [])
        alphabetizable = json.dumps(game["actions"])
        cut = game.get("startingPlayer", 0)
        players = players[cut:] + players[:cut]
        seed_to_games[seed].append([alphabetizable, players, game["id"]])

        count += 1
        if count > stop_short:
            break

    # pylint: disable=consider-using-dict-items
    for seed in seed_to_games:
        parsed = []
        for actions, *suffix in sorted(seed_to_games[seed]):
            parsed.append([json.loads(actions), *suffix])
        seed_to_games[seed] = parsed

    # may later wish to include analysis of deck but currently unused
    return seed_to_games, seed_to_deck

def process_for_players(seed_to_games):
    """docstring"""
    player_to_player_to_scores = {}
    memory = []
    for games in seed_to_games.items():
        # only interested in seeds with multiple games
        if len(games) == 1:
            continue
        gi = iter(games)
        prev = next(gi)
        num_players = len(prev[1])
        for curr in gi:
            for i in range(min(curr, prev)):
                player = curr[1][i % num_players]
                if equal_actions(curr[0][i], prev[0][i]):
                    try:
                        memory[i].append(player)
                    except IndexError:
                        former = prev[1][i % num_players]
                        memory.append([former, player])
                # deal with updating dict and removing from memory
            prev = curr
    return player_to_player_to_scores

def equal_actions(a, b):
    """docstring"""
    return a["type"] == b["type"] and \
        a["target"] == b["target"] and \
        a["value"] == b["value"]

if __name__ == "__main__":
    main()
