"""Tools to check status of and update data. Generally used by scripts in scr"""


from tools import fetch, read, parse


def update_user(username: str):
    """Downloads and stores user summary data, then detects, downloads, and stores data from any 
    games user played not already downloaded."""


    print(f'Fetching game list for {username}...')
    fetch.fetch_user(username)
    print(f'Updated list of {username}\'s games. Searching for games without data...')
    missing_ids = _find_missing_games(username)
    count = len(missing_ids)
    print(f'{count} of {username}\'s games missing game data')
    print(f'Fetching missing data for {count} games...')

    for i, game_id in enumerate(missing_ids):
        if i % 10 == 0:
            print(f'Completed {i} of {count}')
        fetch.fetch_game(game_id)

    print(f'Successfully updated all game data for {username}.')

def update_seed(seed: str):
    """Downloads and stores seed summary data"""


    print(f'Fetching data for {seed}...')
    successful = fetch.fetch_seed(seed)
    if successful:
        print(f'Successfully acquired {seed} data.')


def _find_missing_games(username: str):
    data = read.read_user(username)
    parser = parse.UserData(data)
    missing_ids = []
    for game_id in parser.get_ids():
        if read.game_data_exists(game_id):
            continue
        missing_ids.append(game_id)
    return missing_ids
