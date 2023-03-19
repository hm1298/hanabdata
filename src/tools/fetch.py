import json
import requests
import os
from tools import paths




def _write_json(txt, path):
    with open(path, 'w') as outfile:
        json.dump(json.loads(txt), outfile)

def fetch_games(username: str):
    endpoint = f'https://hanabi.live/api/v1/history-full/{username}'
    response = requests.get(endpoint).text
    path = paths.get_user_data_path(username)
    _write_json(response, path)


def fetch_game(id: str):
    endpoint = f'https://hanabi.live/export/{id}'
    response = requests.get(endpoint).text
    path = paths.get_game_data_path(id)
    _write_json(response, path)

def fetch_seed(seed: str):
    endpoint = f'https://hanabi.live/api/v1/seed-full/{seed}'
    response = requests.get(endpoint).text
    if response == '[]':
        print('Server provided no seed data!')
        return False
    path = paths.get_seed_data_path(seed)
    _write_json(response, path)
    return True
    

    