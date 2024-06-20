"""
This script finds players who take similar actions in identical
gamestates.
"""

import json
from tqdm import tqdm
from hanabdata.tools import structures
from hanabdata.tools.io.read import write_csv
from hanabdata.tools.restriction import get_standard_restrictions

BLOCKED_PLAYERS = {}
HIDDEN_PLAYERS = ["hallmark"]

def main():
    """script execution"""
    # go through all games and create a dictionary of seed names to list of data
    # sort each list by game actions
    res = get_standard_restrictions()
    del res.necessary_constraints["numTurns"]
    seed_to_games, _ = process_for_seeds(res)
    print(len(seed_to_games))
    print(sum(len(x) for x in seed_to_games.values()))
    # go through all seeds and create a double dictionary of players to players to count
    # count the total number of games played, the number of matching gamestates, the number of matching gamestates with similar action chosen (clue<->clue, play<->play), the number of matching gamestates with identical action chosen, the number of matching gamestates with any clue chosen, and the number of matching gamestates with identical clue chosen
    print("starting")
    result = process_for_players(seed_to_games)
    result = filter_data(result, 100)
    print(sum(len(x) for x in result))
    table = parse_data(result)

    # save to file
    write_csv("data/processed/seeds/similar_players.csv", table)

    print("done")

def process_for_seeds(restriction, stop_short=9**9):
    """docstring"""
    gi = structures.FullGamesIterator()

    seed_to_games, seed_to_deck, seed_to_players = {}, {}, {}
    count = 0
    for game in tqdm(gi, total=min(1.5 * stop_short, 1100000)):
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
    for seed in tqdm(seed_to_games):
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
    for games in tqdm(seed_to_games.values()):
        # only interested in seeds with multiple games
        if len(games) == 1:
            continue
        gi = iter(games)
        prev = next(gi)

        # change memory to a list of dicts such that all but the last
        # dict in the list have >=1 keys including the action of the
        # current turn. the last dict must be the last turn of the game
        # or include the first two actions that differ between the
        # current state and the previous state

        # when the gamestate no longer reaches the last element of
        # memory, update player_to_player_to_scores by double iterating
        # over the keys of the last element of memory. continue this
        # for each last element of memory until the current gamestate
        # can update memory successfully

        for curr in gi:
            turn = 0
            limit = min(len(curr[0]), len(prev[0]))
            while turn < limit:
                action1 = tuplify_action(prev[0][turn])
                action2 = tuplify_action(curr[0][turn])
                update_memory(memory, turn, action1, get_player(prev[1], turn))
                update_memory(memory, turn, action2, get_player(curr[1], turn))

                if not equal_actions(curr[0][turn], prev[0][turn]):
                    break
                turn += 1

            clear_memory(memory, player_to_player_to_scores, turn + 1)
            prev = curr

        clear_memory(memory, player_to_player_to_scores, 0)

    return player_to_player_to_scores

def equal_actions(a, b):
    """docstring"""
    return a["type"] == b["type"] and \
        a["target"] == b["target"] and \
        a["value"] == b["value"]

def tuplify_action(a):
    """docstring"""
    return (a["type"], a["target"], a["value"])

def get_player(players, turn):
    """docstring"""
    return players[turn % len(players)]

# TODO: change memory into a class
def update_memory(memory, turn, action, player):
    """mutates memory"""
    try:
        memory[turn][action].add(player)
    except IndexError:
        memory.append({})
        update_memory(memory, turn, action, player)
    except KeyError:
        memory[turn][action] = set()
        update_memory(memory, turn, action, player)

def clear_memory(memory, storage, turn):
    """mutates memory & storage"""
    while len(memory) > turn:
        action_to_players = memory.pop()
        all_players = set().union(*action_to_players.values())
        for these_players in action_to_players.values():
            for player1 in all_players:
                storage.setdefault(player1, {})
                for player2 in these_players:
                    # not interested in similarity of same player
                    if player1 == player2:
                        continue

                    storage[player1].setdefault(player2, [0, 0])

                    # 0th index stores total number of matching gamestates
                    storage[player1][player2][0] += 1
                    if player1 in these_players:
                        # 1st index stores total number of equal actions
                        storage[player1][player2][1] += 1

    return storage

def filter_data(data, limit):
    """docstring"""
    result = {}
    for key1 in data:
        result[key1] = {}
        for key2 in data[key1]:
            counts = data[key1][key2]
            if counts[0] < limit:
                continue
            result[key1][key2] = (*counts, counts[1] / counts[0])
        if len(result[key1]) == 0:
            del result[key1]
    return result

def parse_data(data):
    """docstring"""
    header = ["Player 1", "Player 2", "Total Identical Gamestates", "Total Identical Actions", "Quotient"]
    table = [header]
    for player1 in data:
        for player2 in data[player1]:
            if player1 < player2:
                continue
            row = [player1, player2, *data[player1][player2]]
            table.append(row)

    return table

if __name__ == "__main__":
    main()
