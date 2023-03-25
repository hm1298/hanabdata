""""Handles all calls to hanab.live. Writes to the filesysytem using functions in read.py"""
# pylint: disable=missing-function-docstring

import requests
from tools import read

SITE = "https://hanabi.live"
ROWS = 100  # note the API cannot exceed size of 100

def fetch_user(username: str):
    """Downloads a user's data from hanab.live. First tries to find data already stored inorder to not download 
    duplicate data. If no data is stored, tries to get down load all user data. 
    If hanab.live does not respond in time, attempts to download paginated data."""

    last_id = 0
    if read.user_data_exists(username):
        print(f'found prior data for {username}!')
        prior_data = read.read_user(username)
        last_id = prior_data[0]['id']
        endpoint = f'{SITE}/api/v1/history-full/{username}?start={last_id + 1}'
    else: 
        endpoint = f'{SITE}/api/v1/history-full/{username}'
    try: 
        response = requests.get(endpoint, timeout=15).json()
        
        if read.user_data_exists(username):
            prior_data = read.read_user(username)
        else:
            prior_data = []
        full_data = response + prior_data
        read.write_user(username, full_data)   

    except requests.exceptions.ReadTimeout:
        print('The request timed out! Attempting to use paginated API...')
        fetch_user_paginated(username)

def fetch_user_paginated(username: str):
    """This function is NOT optimized, future proof, or guaranteed to work with all users! 
    Once hanab.live exceeds 10^6 games it will stop working!
    Games likely to also be sorted incorrectly!
    """
    pages = []
    for i in range(10):
        start = i * 100000
        end = (i + 1) * 100000 - 1
        print(f'fetching games with IDs between {start} and {end}')
        endpoint = f'{SITE}/api/v1/history-full/{username}?start={start}&end={end}'
        response = requests.get(endpoint, timeout=15).json()
        pages.append(response)
    all_games = []
    for page in reversed(pages):
        all_games = all_games + page
    read.write_user(username, all_games)
    
def fetch_game(game_id: str):
    endpoint = f'{SITE}/export/{game_id}'
    response = requests.get(endpoint, timeout=15).json()
    read.write_game(game_id, response)

def fetch_seed(seed: str):
    endpoint = f'{SITE}/api/v1/seed-full/{seed}'
    response = requests.get(endpoint, timeout=15).json()
    if response == []:
        print('Server provided no seed data!')
        return False
    read.write_seed(seed, response)
    return True


def _fetch_paginated(url: str, write_func, tag, user_specified_limit=1000000):
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

    write_func(tag, result)
