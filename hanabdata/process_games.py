"""Processes games."""

from datetime import datetime
from hanabdata.tools.io import read
from hanabdata.tools.io.update import update_chunk, update_user
from hanabdata.tools import structures

def get_player_and_seed_info():
    """Gets dict of all players in downloaded games."""
    current = datetime.now()
    player_dict = {}
    seed_dict = {}
    chunk_list = sorted([int(y) for y in read.get_file_names("./data/raw/games")])
    for chunk in chunk_list:
        try:
            data = structures.Chunk.load(chunk)
        except ValueError:
            update_chunk(chunk)
            data = structures.Chunk.load(chunk)
        for game in data:
            if game is None or game == "Error":
                continue
            for player in game["players"]:
                # TODO: make helper function
                if player not in player_dict:
                    player_dict[player] = {
                        "num_games": 1,
                        "last_game": game["id"]
                    }
                else:
                    player_dict[player]["num_games"] += 1
                    player_dict[player]["last_game"] = game["id"]
            seed = game["seed"]
            if seed not in seed_dict:
                seed_dict[seed] = {
                    "num_games": 1,
                    "last_game": game["id"]
                }
            else:
                seed_dict[seed]["num_games"] += 1
                seed_dict[seed]["last_game"] = game["id"]
        if (datetime.now() - current).total_seconds() > 20:
            print(f"Finished processing chunk {chunk}.")
            current = datetime.now()
    read.write_json("./data/player_dict.json", player_dict)
    read.write_json("./data/seed_dict.json", seed_dict)

def analyze_info(info_type):
    """Analyzes existing player info."""
    assert info_type in ("player", "seed")
    data = read.read_json(f"./data/{info_type}_dict.json")

    # laughing emoji
    exactly_one, two_to_nine, ten_to_forty_nine, fifty_to_ninety_nine, hundred_to_nine_nine_nine, thousand_plus = 0, 0, 0, 0, 0, 0
    for player in data:
        num_games = data[player]["num_games"]
        if num_games == 1:
            exactly_one += 1
        elif num_games < 10:
            assert num_games > 0
            two_to_nine += 1
        elif num_games < 50:
            ten_to_forty_nine += 1
        elif num_games < 100:
            fifty_to_ninety_nine += 1
        elif num_games < 1000:
            hundred_to_nine_nine_nine += 1
        else:
            assert num_games >= 1000
            thousand_plus += 1
    print(f"There are {exactly_one} {info_type}s with one game played.")
    print(f"There are {two_to_nine} {info_type}s with 2 to 9 completed games.")
    print(f"There are {ten_to_forty_nine} {info_type}s with 10 to 49 completed games.")
    print(f"There are {fifty_to_ninety_nine} {info_type}s with 50 to 99 completed games.")
    print(f"There are {hundred_to_nine_nine_nine} {info_type}s with 100 to 999 completed games.")
    print(f"There are {thousand_plus} {info_type}s with 1000+ completed games.")

def get_players_with_x_games(req_num_games: int):
    """Returns a dict from player_dict.json with num games filter."""
    data = read.read_json("./data/player_dict.json")
    result = {}
    for player in data:
        if data[player]["num_games"] >= req_num_games:
            result[player] = data[player]
    return result

def update_players(req_num_games: int):
    """Updates all players with at least req_num_games completed."""
    data = get_players_with_x_games(req_num_games)
    num_updates = 0
    current = datetime.now()
    for player in data:
        if (datetime.now() - current).total_seconds() > 20:
            print(f"Updated metagame data for {num_updates} players.")
            current = datetime.now()
        update_user(player, download_games=False)
        num_updates += 1

if __name__ == '__main__':
    get_player_and_seed_info()
    analyze_info("player")
    analyze_info("seed")
    # update_players(1000)
