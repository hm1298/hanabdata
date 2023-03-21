"""Downloads JSONs from Hanab Live's API, then writes to local files."""
# pylint: disable=missing-function-docstring

import json
import requests
from tools import paths

SITE = "https://hanabi.live"
ROWS = 100  # note the API cannot exceed size of 100

def fetch_games(username: str):
    endpoint = f'{SITE}/api/v1/history-full/{username}'
    response = requests.get(endpoint, timeout=15).text
    path = paths.get_user_data_path(username)
    _write_json(response, path)

def fetch_games2(username: str):
    endpoint = f'{SITE}/api/v1/history/{username}?size={ROWS}'
    path = paths.get_user_data_path(username)
    _fetch_paginated(endpoint, path)

def fetch_game(game_id: str):
    endpoint = f'{SITE}/export/{game_id}'
    response = requests.get(endpoint, timeout=15).text
    path = paths.get_game_data_path(game_id)
    _write_json(response, path)

def fetch_seed(seed: str):
    endpoint = f'{SITE}/api/v1/seed-full/{seed}'
    response = requests.get(endpoint, timeout=15).text
    if response == '[]':
        print('Server provided no seed data!')
        return False
    path = paths.get_seed_data_path(seed)
    _write_json(response, path)
    return True



def _fetch_paginated(url: str, write_to: str, user_specified_limit=1000000):
    """Uses the paginated API to download JSON data. Mainly intended for
    pages that are too large to load without pagination.

    Also has a built-in limit on number of pages that may be specified
    with input.
    """
    print("Reached pagination")

    response = requests.get(url, timeout=15).json()
    result = response["rows"]

    page_limit = 1 + (response["total_rows"] - 1) // ROWS
    page_limit = min(page_limit, user_specified_limit)
    for page in range(1, page_limit):
        if page % 5 == 0:
            print(f"On page {page} of {page_limit}")
        new_response = requests.get(url + f'&page={page}', timeout=15)
        new_result = new_response.json()["rows"]
        result.extend(new_result)

    _write_json2(result, write_to)

def _write_json(txt, path):
    with open(path, 'w', encoding="utf8") as outfile:
        json.dump(json.loads(txt), outfile)

def _write_json2(txt, path):
    with open(path, 'w', encoding="utf8") as outfile:
        json.dump(txt, outfile)