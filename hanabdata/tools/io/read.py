"""
This module contains functions for reading and writing data to the file structure 
so that other modules don't have to deal with it. Functions are self-explanatory enough that 
we disable the function docstring check from pylint.  
"""

# pylint: disable=missing-function-docstring
import csv
import json
import pathlib
from os import path


def write(tag, data, data_type = 'user', processing_level = 'raw'):
    file_path = f'./data/{processing_level}/{data_type}s/{tag}'
    if processing_level == 'raw':
        file_path = file_path + '.json'
        _write_json(file_path, data)
    else:
        file_path = file_path + '.csv'
        _write_csv(file_path, data)


class GamesIterator:
    """Iterates over all games metadata"""
    def __init__(self, oldest_to_newest=True):
        dir_path = _get_chunk_meta_path(0)[:-6]
        files = [int(y) for y in get_file_names(dir_path)]
        if oldest_to_newest:
            self.chunk_list = sorted(files, reverse=True)
        else:
            self.chunk_list = sorted(files)

    def set_current(self):
        """Opens the next file and reads as JSON."""
        self.curr_chunk = chunk_num = self.chunk_list.pop()
        self.current = read_chunk(chunk_num, meta=True)
        self.index = 0

    def is_valid(self, game):
        """Retruns True if a game is valid; False otherwise."""
        try:
            game["id"]
        except TypeError:
            return False
        except KeyError:
            print(f"Possible issue with JSON storage in chunk {self.curr_chunk}.")
            return False
        return True

    def __iter__(self):
        self.set_current()
        return self

    def __next__(self):
        while True:
            if self.index == 1000:
                try:
                    self.set_current()
                except IndexError as e:
                    raise StopIteration from e
            game = self.current[self.index]
            self.index += 1
            if self.is_valid(game):
                return game
            



def read_user(username: str):
    user_path = _get_user_data_path(username)
    data = _read_json(user_path)
    return data

def write_user(username: str, data):
    user_path = _get_user_data_path(username)
    _write_json(user_path, data)

def read_seed(seed: str):
    seed_path = _get_seed_data_path(seed)
    data = _read_json(seed_path)
    return data

def write_seed(seed: str, data):
    seed_path = _get_seed_data_path(seed)
    _write_json(seed_path, data)

def read_chunk(chunk: int, meta=False):
    if meta:
        chunk_path = _get_chunk_meta_path(chunk)
    else:
        chunk_path = _get_chunk_path(chunk)
    data = _read_json(chunk_path)
    return data

def write_game_to_chunk(game_id: int, data, meta=False):
    chunk = game_id // 1000
    i = game_id % 1000
    if meta:
        chunk_path = _get_chunk_meta_path(chunk)
    else:
        chunk_path = _get_chunk_path(chunk)
    if not _file_exists(chunk_path):
        data_to_update = [None] * 1000
    else:
        data_to_update = read_chunk(chunk, meta)
    data_to_update[i] = data
    _write_json(chunk_path, data_to_update)

def read_game_from_chunk(game_id: int, meta=False):
    chunk = game_id // 1000
    i = game_id % 1000
    if meta:
        chunk_path = _get_chunk_meta_path(chunk)
    else:
        chunk_path = _get_chunk_path(chunk)
    if not _file_exists(chunk_path):
        return None
    data = read_chunk(chunk, meta)
    return data[i]

def read_games_from_chunk(games: list, chunk: int, meta=False):
    """Assumes games is sorted reverse chronologically.

    Also assumes all entries are >= the least ID in chunk.

    Returns a dict:
        keys - IDs from games, inserted in increasing order
        values - game data for matching ID from file (could be None)
    """
    if meta:
        chunk_path = _get_chunk_meta_path(chunk)
    else:
        chunk_path = _get_chunk_path(chunk)
    if _file_exists(chunk_path):
        try:
            data = read_chunk(chunk, meta)
        except ValueError:
            data = [None] * 1000
    else:
        data = [None] * 1000
    games_dict = {}
    while games and games[-1] < (chunk + 1) * 1000:
        game_id = games.pop()
        assert game_id >= chunk * 1000
        games_dict[game_id] = data[game_id % 1000]
    return games_dict

def write_games_to_chunk(games: dict, chunk: int, meta=False):
    # note file should exist if this function is called. checks anyway
    if meta:
        chunk_path = _get_chunk_meta_path(chunk)
    else:
        chunk_path = _get_chunk_path(chunk)
    if _file_exists(chunk_path):
        try:
            data = read_chunk(chunk, meta)
        except ValueError:
            data = [None] * 1000
    else:
        data = [None] * 1000
    for game_id in games:
        _, i = divmod(game_id, 1000)
        assert _ == chunk  # remove
        data[i] = games[game_id]
    _write_json(chunk_path, data)

def write_user_summary(username: str, summary):
    filepath = _get_user_summary_path(username)
    _write_csv(filepath, summary)

def write_seed_summary(seed: str, summary):
    filepath = _get_seed_summary_path(seed)
    _write_csv(filepath, summary)

def write_winrate_seeds(variant: int, data):
    variant_path = _get_variant_winrate_path(variant)
    _write_csv(variant_path, data)

def write_ratings(type_of_entries, data):
    file_path = f"data/processed/ratings/{type_of_entries}.csv"
    _write_csv(file_path, data)

def seed_data_exists(seed: str):
    seed_path = _get_seed_data_path(seed)
    return _file_exists(seed_path)

def user_data_exists(username: str):
    user_path = _get_user_data_path(username)
    return _file_exists(user_path)

def read_game_ids(username: str):
    data = read_user(username)
    return [game["id"] for game in data]


def write_score_hunt(username: str, data):
    score_hunt_path = _get_score_hunt_path(username)
    _write_csv(score_hunt_path, data)

def write_score_hunt_summary(data):
    # Note Hanab Live does not permit usernames with '(' or ')', so
    # there is no risk of collision.
    write_score_hunt("(SUMMARY)", data)


def get_file_names(path: str):
    """Returns a list of JSON files in the given directory."""
    file_list = []
    folder = pathlib.Path(path)
    for file in folder.glob("*.json"):
        file_list.append(file.name[:-5])
    return file_list

def get_users():
    """Returns a list of usernames."""
    return get_file_names("./data/raw/users")

def get_game_ids():
    """Returns a list of game IDs from the old format."""
    return get_file_names("./data/raw/games")

def get_score_hunt(username: str):
    hunt_path = f'./data/processed/score_hunts/{username}.csv'
    if not _file_exists(hunt_path):
        return None
    return _read_csv(hunt_path)


def _file_exists(filepath: str):
    return path.isfile(filepath)

def _get_user_data_path(username: str):
    return f'./data/raw/users/{username}.json'

def _get_seed_data_path(seed: str):
    return f'./data/raw/seeds/{seed}.json'

def _get_chunk_path(chunk: int):
    return f'./data/raw/games/{chunk}.json'

def _get_chunk_meta_path(chunk: int):
    return f'./data/preprocessed/games/{chunk}.json'

def _get_user_summary_path(username: str):
    return f'./data/processed/users/{username}.csv'

def _get_game_summary_path(game_id: int):
    return f'./data/processed/games/{game_id}.csv'

def _get_variant_winrate_path(variant_id: int):
    return f'./data/processed/variants/winrates/{variant_id}.csv'

def _get_seed_summary_path(seed: str):
    return f'./data/processed/seeds/{seed}.csv'

def _get_score_hunt_path(username: str):
    return f'./data/processed/score_hunts/{username}.csv'


# Read and write JSONs and CSVs

def _read_json(file_path):
    with open(file_path, encoding="utf8") as json_file:
        try:
            data = json.load(json_file)
        except BaseException as e:
            print(e)
            print(f"The offending file is found at: {file_path}")
            raise e
    return data

def _write_json(file_path, txt):
    with open(file_path, 'w', encoding="utf8") as outfile:
        json.dump(txt, outfile)

def _read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        return list(csvreader)

def _write_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(data)