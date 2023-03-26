"""
This module contains functions for reading and writing data to the file structure 
so that other modules don't have to deal with it. Functions are self-explanatory enough that 
we disable the function docstring check from pylint.  
"""

# pylint: disable=missing-function-docstring
import json
import csv
from os import path


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


def read_game_chunk(chunk: int):
    chunk_path = _get_game_chunk_path(chunk)
    data = _read_json(chunk_path)
    return data

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



def _file_exists(filepath: str):
    return path.isfile(filepath)

def _get_user_data_path(username: str):
    return f'./data/raw/users/{username}.json'

def _get_game_data_path(game_id: int):
    return f'./data/raw/games/{game_id}.json'

def _get_seed_data_path(seed: str):
    return f'./data/raw/seeds/{seed}.json'

def _get_game_chunk_path(chunk: int):
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

def _read_json(file_path):
    with open(file_path, encoding="utf8") as json_file:
        data = json.load(json_file)
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