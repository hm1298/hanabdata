"""Downloads JSONs from Hanab Live's API, then writes to local files."""
# pylint: disable=missing-function-docstring

import json
import requests
from tools import paths

SITE = "https://hanabi.live/api/v1"
ROWS = 100  # note the API cannot exceed size of 100
MAX_TIME = 12

def fetch_games(username: str):
    endpoint = f'{SITE}/history-full/{username}'
    response = requests.get(endpoint, timeout=MAX_TIME).text
    path = paths.get_user_data_path(username)
    _write_json(response, path)

def fetch_games2(username: str):
    endpoint = f'{SITE}/history/{username}?size={ROWS}'
    path = paths.get_user_data_path(username)
    _fetch_paginated(endpoint, path)

def fetch_game(game_id: str):
    endpoint = f'https://hanabi.live/export/{game_id}'
    response = requests.get(endpoint, timeout=MAX_TIME).text
    path = paths.get_game_data_path(game_id)
    _write_json(response, path)

def fetch_seed(seed: str):
    endpoint = f'{SITE}/seed-full/{seed}'
    response = requests.get(endpoint, timeout=MAX_TIME).text
    if response == '[]':
        print('Server provided no seed data!')
        return False
    path = paths.get_seed_data_path(seed)
    _write_json(response, path)
    return True

def find_given_game(url: str, given: int):
    """Returns the nth Game ID in the API. Returns none if too large."""
    safe_url = url.replace("-full", "") + f'?size={ROWS}'
    response = requests.get(safe_url, timeout=MAX_TIME).json()
    num_games = response["rows"]

    if given > num_games:
        return

    response = requests.get


def _fetch_paginated(url: str, write_to: str, max_games=None):
    """Uses the paginated API to download JSON data. Mainly intended for
    pages that are too large to load without pagination.

    Also can limit number of games downloaded. If the limit applies,
    then the oldest games will be downloaded.
    """
    print("Reached pagination")

    if max_games:
        game_id_limit = find_nth_game(url, max_games)

    response = requests.get(url, timeout=MAX_TIME).json()
    result = response["rows"]

    page_limit = 1 + (response["total_rows"] - 1) // ROWS
    page_limit = min(page_limit, max_games)
    for page in range(1, page_limit):
        if page % 5 == 0:
            print(f"On page {page} of {page_limit}")
        new_response = requests.get(url + f'&page={page}', timeout=MAX_TIME)
        new_result = new_response.json()["rows"]
        result.extend(new_result)

    _write_json2(result, write_to)

def _write_json(txt, path):
    with open(path, 'w', encoding="utf8") as outfile:
        json.dump(json.loads(txt), outfile)

def _write_json2(txt, path):
    with open(path, 'w', encoding="utf8") as outfile:
        json.dump(txt, outfile)
