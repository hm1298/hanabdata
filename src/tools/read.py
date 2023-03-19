from tools import paths
import json
import csv


def read_games(username: str):
    path = paths.get_user_data_path(username)
    data = _read_json(path)
    return data

def read_game(id: int):
    path = paths.get_game_data_path(id)
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
    with open(path) as f:
        data = json.load(f)
    return data

def _write_csv(path, data):
    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(data)
 