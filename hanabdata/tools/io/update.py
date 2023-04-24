"""Tools to check status of and update data. Generally used by scripts"""
from datetime import datetime
from . import fetch, read

def update_user(username: str):
    """Downloads and stores user summary data, then detects, downloads, and stores data from any 
    games user played not already downloaded."""

    print('Gathering prior data...')
    if read.user_data_exists(username):
        prior_data = read.read_user(username)
        start = prior_data[0]['id'] + 1
        print('Found prior data')
    else:
        prior_data = []
        start = 0
        print('No prior data found')

    print(f'Requesting {username}\'s data starting from {start}' )
    new_data = fetch.fetch_user(username, start)
    print(f'Received data for {len(new_data)} new games')
    full_data = new_data + prior_data
    read.write_user(username, full_data)

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
        read.write_seed(seed, data)

def update_game(game_id: int):
    """Updates a specific game."""
    data = fetch.fetch_game(game_id)
    read.write_game_to_chunk(game_id, data)


def update_chunk(chunk_number: int, exceptional_ids=None, exclude=True):
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

    games_dict = read.read_games_from_chunk(ids, ids[-1] // 1000)
    for game_id, game in games_dict.items():
        if game is None:
            games_dict[game_id] = fetch.fetch_game(game_id)
            num_updated += 1
        if (datetime.now() - current).total_seconds() > 20:
            print(f"Fetched game with ID {game_id}, the {num_updated}th",
                "update in this chunk since last print message.")
            current, num_updated = datetime.now(), 0
    read.write_games_to_chunk(games_dict, chunk_number)


def _find_missing_games(username: str):
    """Iterates over chunks based on ids."""
    data = read.read_user(username)
    ids = sorted([row["id"] for row in data], reverse=True)
    missing_ids = []
    while ids:
        games_dict = read.read_games_from_chunk(ids, ids[-1] // 1000)
        for game_id, game in games_dict.items():
            if game is None:
                missing_ids.append(game_id)
    return missing_ids
