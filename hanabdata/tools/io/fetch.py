""""Handles all calls to hanab.live. Returns JSONs."""

import requests

SITE = "https://hanab.live/api/v1"
ROWS = 100  # note the API cannot exceed size of 100
MAX_TIME = 10
CHUNK_SIZE = 2048

# strictly speaking, it's more helpful to pass in BOTH the number of
# games that have been downloaded AND the lowest possible game ID of an
# "undownloaded" game. not sure what dependencies, so leaving for now
def fetch_user(username: str, start_id = 0):
    """Downloads a user's data from Hanab Live.

    First, checks lesser API for the size of the download. If it does
    not exceed 2 * CHUNK_SIZE, then attempts to download from full API
    without pagination.

    If the server does not respond before MAX_TIME, enters pagination
    and downloads in chunks.

    Returns data sorted in the order delivered by the server: reverse
    chronologically.
    """
    endpoint = f'{SITE}/history-full/{username}'
    # This adds a constant amount of time (~0.3-1 seconds) to each call
    # but saves MAX_TIME seconds on large users.
    start_guess = find_given_game(endpoint, 2 * CHUNK_SIZE)
    if start_guess <= start_id:
        attempted_fetch, errored = fetch_url(endpoint + f'?start={start_id}')
        if not errored:
            return attempted_fetch
    return fetch_in_chunks(endpoint, start_id)

def fetch_in_chunks(url: str, lower_limit: int, num_rows=CHUNK_SIZE, end=None):
    """Downloads a user's data in request sizes of num_rows or less.

    Checks lesser API for game IDs and paginates full API based on
    those ranges, with num_rows games per page.

    Pulls games in reverse chronological order. Will likely break if
    API no longer delivers in that order!
    """
    result, game_index = [], num_rows
    while True:
        start = find_given_game(url, game_index)
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
        attempted_fetch, errored = fetch_url(endpoint)
        if errored:
            if num_rows < 100:
                print(f"Chunk size of {num_rows} is too low.")
                raise AssertionError("It appears the site is down..")
            print(f"Reducing chunk size to {num_rows//2}")
            return result + fetch_in_chunks(url, lower_limit, \
                num_rows=num_rows//2, end=end)
        result += attempted_fetch
        if start == 0:
            break
        game_index += num_rows
        end = start - 1
    return result

def fetch_url(url, verbose=True):
    """Attempts to fetch from Hanab Live.

    Returns a tuple of two items:
        - JSON object that was downloaded, defaults to empty list
        - Exception type if an error occurred, else None
    """
    try:
        if verbose:
            print(f"Fetching from {url}")
        response = requests.get(url, timeout=MAX_TIME)
        try:
            data = response.json()
        except ValueError as exc:
            if response.text[:5] == "Error":
                return "Error", None
            print(f"ERROR: {url} failed to return a valid JSON object.")
            print("Unexpected error message from site:\n")
            print(response.text + "\n")
            raise exc
        return data, None
    except BaseException as e:
        print(f"Unable to complete request to {url}")
        return [], e

def fetch_game(game_id: str):
    """Fetches a game. Raises error if unable."""
    endpoint = f'https://hanabi.live/export/{game_id}'
    return _fetch_url_or_error(endpoint)

def fetch_seed(seed: str):
    """Fetches a seed. Raises error if unable."""
    endpoint = f'{SITE}/seed-full/{seed}'
    return _fetch_url_or_error(endpoint)

def find_given_game(url: str, given: int):
    """Returns the nth Game ID in the API.

    Returns 0 if too large.
    """
    page_num, page_index = divmod(given - 1, ROWS)
    safe_url = url.replace("-full", "") + f'?size={ROWS}&page={page_num}'
    response = _fetch_url_or_error(safe_url)
    if response == "Error":
        return 0
    game_list = response["rows"]
    if game_list is None or len(game_list) <= page_index:
        return 0
    return game_list[page_index]["id"]


# DO NOT DELETE
# TODO: turn into public method that can download from lesser API,
# which may be necessary to retrieve some data (for instance, variants
# does not have a full API).
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

    response, _ = fetch_url(url)
    result = response["rows"]

    page_limit = 1 + (response["total_rows"] - 1) // ROWS
    page_limit = min(page_limit, max_games)
    for page in range(1, page_limit):
        if page % 5 == 0:
            print(f"On page {page} of {page_limit}")
        new_response, _ = fetch_url(url + f'&page={page}')
        new_result = new_response.json()["rows"]
        result.extend(new_result)
    return result

def _fetch_url_or_error(url, verbose=False):
    """Fetches URL. Raises error if unable."""
    response, error = fetch_url(url, verbose)
    if error:
        raise error
    return response
