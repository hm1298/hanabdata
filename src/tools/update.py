from tools import fetch, read, parse, paths

def update_user(username: str):
    print(f'Fetching game list for {username}...')
    fetch.fetch_games(username)
    print(f'Updated list of {username}\'s games. Searching for games without data...')
    missing_ids = _find_missing_games(username)
    count = len(missing_ids)
    print(f'{count} of {username}\'s games missing game data')
    print(f'Fetching missing data for {count} games...')
    
    for i, id in enumerate(missing_ids):
        if i % 10 == 0:
            print(f'Completed {i} of {count}')
        fetch.fetch_game(id)
        
    print(f'Successfully updated all game data for {username}.')

def _find_missing_games(username: str):
    data = read.read_games(username)
    parser = parse.UserData(data)
    missing_ids = []
    for id in parser.get_ids():
        if paths.game_data_exists(id):
            continue
        missing_ids.append(id)
    return missing_ids

def update_seed(seed: str):
    
    print(f'Fetching data for {seed}')
    fetch.fetch_seed(seed)
    print(f'Completed successfully')
    