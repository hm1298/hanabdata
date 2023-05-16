"""Helper module for moving games info from preprocessed to raw."""

from hanabdata.tools.io import read
from hanabdata.tools.io.fetch import fetch_seed
from hanabdata.tools.io.update import update_metagames

def populate_metagame_info(games):
    """Finds metagame info from user or seed. Saves to file."""
    for game in games:
        if game is None:
            continue
        try:
            game_id = game["id"]
        except KeyError:
            continue
        metadata = read.read_game_from_chunk(game_id, True)
        if metadata is not None:
            continue

        seed = game["seed"]
        players = game["players"]
        for player in players:
            update_metagames(player)

        metadata = read.read_game_from_chunk(game_id, True)
        if metadata is not None:
            continue
        for game2 in fetch_seed(seed):
            if game2["id"] == game_id:
                read.write_game_to_chunk(game_id, game2, True)
                break

def iter_over_all_games():
    """A generator over all games."""

if __name__ == "__main__":
    game_path = "./data/raw/games/"
    for file_name in read.get_file_names(game_path):
        print("hi")
        games_list = read._read_json(game_path + file_name + ".json")
        populate_metagame_info(games_list)
