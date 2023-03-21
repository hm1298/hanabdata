"""
This module connects anything that wants to read or write data to the module handling filepaths. 
It could be better for these two modules to be merged into one.
"""
# pylint: disable=missing-function-docstring
import json
import csv
from tools import paths

def read_games(username: str):
    path = paths.get_user_data_path(username)
    data = _read_json(path)
    return data

def read_game(game_id: int):
    path = paths.get_game_data_path(game_id)
    data = _read_json(path)
    return data

def read_game_ids(username: str):
    data = read_games(username)
    return [game["id"] for game in data]

def read_seed(seed: str):
    path = paths.get_seed_data_path(seed)
    data = _read_json(path)
    return data

def write_user_summary(username: str, summary):
    filepath = paths.get_user_summary_path(username)
    _write_csv(filepath, summary)

def write_seed_summary(seed: str, summary):
    filepath = paths.get_seed_summary_path(seed)
    _write_csv(filepath, summary)


def write_winrate_seeds(variant: int, data):
    path = paths.get_variant_winrate_path(variant)
    _write_csv(path, data)



def _read_json(path):
    with open(path, encoding="utf8") as json_file:
        data = json.load(json_file)
    return data

def _write_csv(path, data):
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(data)
 