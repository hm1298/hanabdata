import fetch
import read
import parse
import paths



def update_user(username: str):
    print(f'Fetching game list for {username}...')
    fetch.fetch_games(username)
    print(f'Updated game list. Searching database for missing games...')
    missing_ids = find_missing_games(username)
    count = len(missing_ids)
    print(f'Fetching missing data for {count} games...')
    
    for i, id in enumerate(missing_ids):
        if i % 10 == 0:
            print(f'Completed {i} of {count}')
        fetch.fetch_game(id)
        
    print(f'Successfully updated all game data for {username}.')


def find_missing_games(username: str):
    data = read.read_games(username)
    parser = parse.UserData(data)
    missing_ids = []
    for id in parser.get_ids():
        if paths.game_data_exists(id):
            continue
        missing_ids.append(id)
    return missing_ids


def update_seed_data():
    for i in range(100):
        seed = f'p2v0s{i + 1}'
        fetch.fetch_seed(seed)



if __name__ == '__main__':
    #username = 'sjdrodge'
    #update_user(username)
    update_seed_data()