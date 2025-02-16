"""Tools to check status of and update data. Generally used by scripts"""
from datetime import datetime
from . import fetch, read
from .. import structures

def update_user(username: str, download_games=True):
    """Downloads and stores user summary data, then detects, downloads, and stores data from any 
    games user played not already downloaded."""

    print('Gathering prior data...')
    try:
        prior_data = structures.User.load(username).data
        start = prior_data[0]['id'] + 1
        print(f'Found prior data containing {len(prior_data)} games')
    except structures.DatabaseError:
        prior_data = []
        start = 0
        print('No prior data found')


    print(f'Requesting {username}\'s data starting from {start}' )
    new_data = fetch.fetch_user(username, start)
    if new_data == "Error":
        print("An error has occurred. User may have deleted their account", 
              "or account may have never existed.")
        return
    print(f'Received data for {len(new_data)} new games')
    full_data = structures.User(new_data + prior_data, username)
    full_data.save()
    #read.write_user(username, full_data)
    update_metagames(username)

    if download_games:
        missing_ids = _find_missing_games(username)
        count = len(missing_ids)
        print(f'{count} of {username}\'s games missing game data')
        print(f'Requesting data for {count} games...')

        for i, game_id in enumerate(missing_ids):
            if i % 10 == 0:
                print(f'Completed {i} of {count}')
            update_game(game_id)

        print(f'Successfully updated all game data for {username}.')

def update_seed(seed: str):
    """Downloads and stores seed summary data"""
    print(f'Fetching data for {seed}...')
    data = fetch.fetch_seed(seed)
    if data == []:
        print('Server provided no seed data')
    else:
        structures.Seed(data, seed).save()


def update_game(game_id: int):
    """Updates a specific game."""
    data = fetch.fetch_game(game_id)
    structures.Game(data, game_id).save()

def update_chunk(chunk_number: int, exceptional_ids=None, exclude=True, end_on_error=False):
    """Updates all games in a chunk."""
    print(f"Updating games between {chunk_number * 1000} and",
        f"{chunk_number * 1000 + 999}.")
    current, num_updated = datetime.now(), 0
    if exceptional_ids is None:
        exceptional_ids = []

    ids = []
    for i in range(1000 * (chunk_number + 1), 1000 * chunk_number, -1):
        game_id = i - 1
        if exclude:
            # inefficient
            if game_id not in exceptional_ids:
                ids.append(game_id)
        else:
            # inefficient
            if game_id in exceptional_ids:
                ids.append(game_id)

    games_dict = read.read_games_from_chunk(ids, ids[-1] // 1000) # broken -- unsure how to fix
    for game_id, game in games_dict.items():
        if game is None:
            response = fetch.fetch_game(game_id)
            if end_on_error and response == "Error":
                read.write_games_to_chunk(games_dict, chunk_number)
                print(f"Stopped downloading after nonexistent game {game_id}.")
                return "Please stop"
            games_dict[game_id] = response
            num_updated += 1
        if (datetime.now() - current).total_seconds() > 20:
            print(f"Fetched game with ID {game_id}, update number {num_updated}",
                "in this chunk since last print message.")
            current, num_updated = datetime.now(), 0
    read.write_games_to_chunk(games_dict, chunk_number)

def update_chunk2(chunk_number: int, exceptional_ids=None, exclude=True, end_on_error=False):
    """Updates all games and metagames in a chunk."""
    print(f"Updating games between {chunk_number * 1000} and",
        f"{chunk_number * 1000 + 999}.")
    current, num_updated = datetime.now(), 0
    if exceptional_ids is None:
        exceptional_ids = []

    ids = []
    for i in range(1000 * (chunk_number + 1), 1000 * chunk_number, -1):
        game_id = i - 1
        if exclude:
            # inefficient
            if game_id not in exceptional_ids:
                ids.append(game_id)
        else:
            # inefficient
            if game_id in exceptional_ids:
                ids.append(game_id)

    meta_ids = ids[::]

    games_dict = read.read_games_from_chunk(ids, ids[-1] // 1000)
    meta_dict = read.read_games_from_chunk(meta_ids, meta_ids[-1] // 1000, meta=True)
    for game_id, game in games_dict.items():
        exit_loop = False
        if game is None:
            response = fetch.fetch_game(game_id)
            if end_on_error and response == "Error":
                print(f"Stopped downloading after nonexistent game {game_id}.")
                exit_loop = True
                break
            games_dict[game_id] = response

            if response == "Error":
                print("Unable to access metadata for game {game_id}.")
                exit_loop = True
                break
            response2 = fetch.fetch_metagame(game_id, games_dict[game_id]["players"][0])
            if end_on_error and response2 == "Error":
                print(f"Stopped downloading after nonexistent metadata for game {game_id}.")
                exit_loop = True
                break
            meta_dict[game_id] = response2

            num_updated += 1
        if (datetime.now() - current).total_seconds() > 20:
            print(f"Fetched game with ID {game_id}, update number {num_updated}",
                "in this chunk since last print message.")
            current, num_updated = datetime.now(), 0
        if exit_loop:
            break
    read.write_games_to_chunk(games_dict, chunk_number)
    read.write_games_to_chunk(meta_dict, chunk_number, meta=True)
    if exit_loop:
        return "Please stop"


def update_metagames(username: str):
    """Iterates over chunks based on ids."""
    try:
        data = structures.User.load(username)
    except LookupError:
        # data = fetch.fetch_user(username)
        # if data == "Error":
        #     return
        # read.write_user(username, data)
        return
    id_lookup = {}
    for game in data:
        id_lookup[game["id"]] = game

    ids = _find_missing_games(username, True)
    try:
        chunk, buffer = ids[0] // 1000, {}
    except IndexError:
        return

    for game_id in ids:
        curr_chunk = game_id // 1000
        if chunk != curr_chunk:
            read.write_games_to_chunk(buffer, chunk, True)
            chunk, buffer = curr_chunk, {}
        buffer[game_id] = id_lookup[game_id]

# TODO: Change some of these to work on dicts rather than usernames.

def _find_missing_games(username: str, meta=False):
    """Iterates over chunks based on ids."""
    data = structures.User.load(username)
    ids = sorted([row["id"] for row in data], reverse=True)
    missing_ids = []
    while ids:
        games_dict = read.read_games_from_chunk(ids, ids[-1] // 1000, meta)
        for game_id, game in games_dict.items():
            if game is None:
                missing_ids.append(game_id)
    return missing_ids
