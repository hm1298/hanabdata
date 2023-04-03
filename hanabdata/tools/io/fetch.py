""""Handles all calls to hanab.live. Returns JSONs."""

import requests

SITE = "https://hanab.live/api/v1"
ROWS = 100  # note the API cannot exceed size of 100
MAX_TIME = 8
CHUNK_SIZE = 2048

# strictly speaking, it's more helpful to pass in BOTH the number of
# games that have been downloaded AND the lowest possible game ID of an
# "undownloaded" game. not sure what dependencies, so leaving for now
def fetch_user(username: str, start_id = 0):
    """Downloads a user's data from hanab.live. First tries to find data already stored inorder to not download 
    duplicate data. If no data is stored, tries to get down load all user data. 
    If hanab.live does not respond in time, attempts to download paginated data."""
    endpoint = f'{SITE}/history-full/{username}'
    attempted_fetch, status = fetch_url(endpoint + f'?start={start_id}')
    if status:
        return attempted_fetch
    return fetch_in_chunks(endpoint, start_id)

def fetch_in_chunks(url: str, lower_limit: int, num_rows=CHUNK_SIZE, end=None):
    """Checks lesser API for game IDs and paginates full API based on
    those ranges, with num_rows games per page. Pulls games in reverse chronological order.
    """
    result, game_index = [], num_rows
    while True:
        start, next_end = find_given_game(url, game_index)
        endpoint = url + f'?start={max(start, lower_limit)}'
        if end is not None:
            # CURRENTLY, THE CODE WILL ERROR IF IT FINDS A GOOD CHUNK
            # SIZE BUT THEN RUNS INTO A PROBLEM LATER--FOR INSTANCE, IF
            # THE SERVER STARTS LIMITING REQUESTS. THIS IS AN EASY FIX,
            # BUT IT IS NOT YET CODED!
            if end < start:
                print("Something strange happened..")
                raise AssertionError("end < start")
            endpoint += f'&end={end}'
        attempted_fetch, status = fetch_url(endpoint)
        if not status:
            if num_rows < 100:
                print(f"Chunk size of {num_rows} is too low.")
                raise AssertionError("It appears the site is down..")
            print(f"Reducing chunk size to {num_rows//2}")
            return result + fetch_in_chunks(url, lower_limit, \
                num_rows=num_rows//2, end=end)
        result += attempted_fetch
        if next_end is None:
            break
        game_index += num_rows
        end = next_end
    return result

def fetch_url(url):
    """Attempts to fetch from Hanab Live.

    Returns a list of JSONs (dicts) if successful.

    Handles errors. Returns None if unsuccessful.
    """
    try:
        print(f"Fetching from {url}")
        return requests.get(url, timeout=MAX_TIME).json(), True
    except requests.exceptions.ReadTimeout:
        print(f"Unable to connect to {url}")
        return [], False


def fetch_game(game_id: str):
    """Fetches a game."""
    endpoint = f'https://hanabi.live/export/{game_id}'
    response = requests.get(endpoint, timeout=MAX_TIME).json()
    return response

def fetch_seed(seed: str):
    """Fetches a seed."""
    endpoint = f'{SITE}/seed-full/{seed}'
    response = requests.get(endpoint, timeout=MAX_TIME).json()
    return response

def find_given_game(url: str, given: int):
    """Returns the nth and an adjacent Game ID in the API.

    Chooses the adjacent game to be larger if both are on the same page
    of the paginated API. Otherwise, chooses the smaller game. Chooses
    None if no such game exists.

    Returns a tuple (x, y) such that x > y or y is None.

    Returns 0 if too large.
    """
    page_num, page_index = divmod(given - 1, ROWS)
    safe_url = url.replace("-full", "") + f'?size={ROWS}&page={page_num}'
    response = requests.get(safe_url, timeout=MAX_TIME).json()
    game_list = response["rows"]
    if game_list is None or len(game_list) <= page_index:
        return 0, None
    if len(game_list) > page_index:
        if page_index == 0:
            return game_list[0]["id"], None
        return game_list[page_index - 1]["id"], game_list[page_index]["id"]
    return game_list[page_index]["id"], game_list[page_index + 1]["id"]

def _fetch_paginated(url: str, write_to: str, max_games=None):
    """Uses the paginated API to download JSON data. Mainly intended for
    pages that are too large to load without pagination.

    Also can limit number of games downloaded. If the limit applies,
    then the oldest games will be downloaded.
    """
    print("Reached pagination")

    if max_games:
        game_id_limit = find_given_game(url, max_games)
        page_limit = game_id_limit
    # method needs to be edited or deleted

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
