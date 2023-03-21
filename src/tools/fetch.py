"""Downloads JSONs from Hanab Live's API, then writes to local files."""
# pylint: disable=missing-function-docstring

import json
import requests
from tools import paths

def fetch_games(username: str):
    endpoint = f'https://hanabi.live/api/v1/history-full/{username}'
    response = requests.get(endpoint, timeout=15).text
    path = paths.get_user_data_path(username)
    _write_json(response, path)


def fetch_game(game_id: str):
    endpoint = f'https://hanabi.live/export/{game_id}'
    response = requests.get(endpoint, timeout=15).text
    path = paths.get_game_data_path(game_id)
    _write_json(response, path)

def fetch_seed(seed: str):
    endpoint = f'https://hanabi.live/api/v1/seed-full/{seed}'
    response = requests.get(endpoint, timeout=15).text
    if response == '[]':
        print('Server provided no seed data!')
        return False
    path = paths.get_seed_data_path(seed)
    _write_json(response, path)
    return True

def _write_json(txt, path):
    with open(path, 'w', encoding="utf8") as outfile:
        json.dump(json.loads(txt), outfile)
