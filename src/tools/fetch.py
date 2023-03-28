""""Handles all calls to hanab.live. Returns JSONs."""
# pylint: disable=missing-function-docstring

import requests

SITE = "https://hanabi.live/api/v1"
ROWS = 100  # note the API cannot exceed size of 100
MAX_TIME = 12

def fetch_user(username: str, start_id = 0):
    """Downloads a user's data from hanab.live. First tries to find data already stored inorder to not download 
    duplicate data. If no data is stored, tries to get down load all user data. 
    If hanab.live does not respond in time, attempts to download paginated data."""

    if start_id > 0:    
        endpoint = f'{SITE}/history-full/{username}?start={start_id}'
    else: 
        endpoint = f'{SITE}/history-full/{username}'
    try: 
        response = requests.get(endpoint, timeout=15).json()
        return response  
    except requests.exceptions.ReadTimeout:
        print('The request timed out! Attempting to to split games into smaller chunks...')
        return fetch_user_chunk(username, min_id = start_id)

def fetch_user_chunk(username: str, min_id = 0, max_id = 1000000, increment = 100000):
    """
    This function is NOT optimized, future proof, or guaranteed to work with all users! 
    Once hanab.live exceeds 10^6 games it will stop working!
    Games likely to also be sorted incorrectly!
    """
    start = min_id
    next_start = min_id + increment
    end = next_start - 1
    data = []
    
    while True:
        end = min(end, max_id)
        print(f'fetching games with IDs between {start} and {end}')
        
        endpoint = f'{SITE}/history-full/{username}?start={start}&end={end}'
        try: 
            response = requests.get(endpoint, timeout=15).json()
        except requests.exceptions.ReadTimeout as error:
            if increment <= 1000:
                raise ConnectionError('The request timed out! \
                                      This is either your internet or the server being slow') from error
            print('The request timed out! This could be due to asking the server for too much. \
                  Attempting to split request into smaller chunks...')
            response = fetch_user_chunk(username, min_id = start, max_id = end, increment = increment // 10)
        data = response + data
        if end == max_id:
            break

    return data
        
def fetch_game(game_id: str):
    endpoint = f'https://hanabi.live/export/{game_id}'
    response = requests.get(endpoint, timeout=MAX_TIME).json()
    return response

def fetch_seed(seed: str):
    endpoint = f'{SITE}/seed-full/{seed}'
    response = requests.get(endpoint, timeout=MAX_TIME).json()
    return response

def find_given_game(url: str, given: int):
    """Returns the nth Game ID in the API. Returns none if too large."""
    safe_url = url.replace("-full", "") + f'?size={ROWS}'
    response = requests.get(safe_url, timeout=MAX_TIME).json()
    num_games = response["rows"]

    if given > num_games:
        return

    #response = requests.get  #broken code, fix


def _fetch_paginated(url: str, write_to: str, max_games=None):
    """Uses the paginated API to download JSON data. Mainly intended for
    pages that are too large to load without pagination.

    Also can limit number of games downloaded. If the limit applies,
    then the oldest games will be downloaded.
    """

    
    print("Reached pagination")

    if max_games:
        game_id_limit = find_given_game(url, max_games)

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
    return result
