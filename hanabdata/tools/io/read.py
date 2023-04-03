"""
This module contains functions for reading and writing data to the file structure 
so that other modules don't have to deal with it. Functions are self-explanatory enough that 
we disable the function docstring check from pylint.  
"""

# pylint: disable=missing-function-docstring
import json
import csv
from os import path, listdir


def write(tag, data, data_type = 'user', processing_level = 'raw'):
    file_path = f'./data/{processing_level}/{data_type}s/{tag}'
    if processing_level == 'raw':
        file_path = file_path + '.json'
        _write_json(file_path, data)
    else:
        file_path = file_path + '.csv'
        _write_csv(file_path, data)



def read_user(username: str):
    user_path = _get_user_data_path(username)
    data = _read_json(user_path)
    return data

def write_user(username: str, data):
    user_path = _get_user_data_path(username)
    _write_json(user_path, data)

def read_game(game_id: int):
    game_path = _get_game_data_path(game_id)
    data = _read_json(game_path)
    return data

def write_game(game_id: int, data):
    game_path = _get_game_data_path(game_id)
    _write_json(game_path, data)

def read_seed(seed: str):
    seed_path = _get_seed_data_path(seed)
    data = _read_json(seed_path)
    return data

def write_seed(seed: str, data):
    seed_path = _get_seed_data_path(seed)
    _write_json(seed_path, data)

def read_chunk(chunk: int):
    chunk_path = _get_chunk_path(chunk)
    data = _read_json(chunk_path)
    return data

def write_game_to_chunk(game_id: int, data):
    chunk = game_id // 1000
    i = game_id % 1000
    chunk_path = _get_chunk_path(chunk)
    if not _file_exists(chunk_path):
        data_to_update = [None] * 1000
    else:
        data_to_update = read_chunk(chunk)
    data_to_update[i] = data
    _write_json(chunk_path, data_to_update)

def read_game_from_chunk(game_id: int):
    chunk = game_id // 1000
    i = game_id % 1000
    chunk_path = _get_chunk_path(chunk)
    if not _file_exists(chunk_path):
        return None
    data = read_chunk(chunk)
    return data[i]

def write_user_summary(username: str, summary):
    filepath = _get_user_summary_path(username)
    _write_csv(filepath, summary)

def write_seed_summary(seed: str, summary):
    filepath = _get_seed_summary_path(seed)
    _write_csv(filepath, summary)

def write_winrate_seeds(variant: int, data):
    varaint_path = _get_variant_winrate_path(variant)
    _write_csv(varaint_path, data)

def game_data_exists(game_id: int):
    game_path = _get_game_data_path(game_id)
    return _file_exists(game_path)

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


def get_game_ids():
    games_path = './data/raw/games'
    file_names = listdir(games_path)
    game_ids = []
    for file_name in file_names:
        if file_name == '.gitkeep':
            continue
        game_ids.append(int(file_name[0:-5]))
    return game_ids

def get_score_hunt(username: str):
    hunt_path = f'./data/processed/score_hunts/{username}.csv'
    if not _file_exists(hunt_path):
        return None
    return _read_csv(hunt_path)


def _file_exists(filepath: str):
    return path.isfile(filepath)

def _get_user_data_path(username: str):
    return f'./data/raw/users/{username}.json'

def _get_game_data_path(game_id: int):
    return f'./data/raw/games/{game_id}.json'

def _get_seed_data_path(seed: str):
    return f'./data/raw/seeds/{seed}.json'

def _get_chunk_path(chunk: int):
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
        return [row for row in csvreader]

def _write_csv(file_path, data):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(data)