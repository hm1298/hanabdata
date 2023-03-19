from os import path


def get_user_data_path(username: str):
    return f'./data/raw/users/{username}.json'

def get_game_data_path(id: int):
    return f'./data/raw/games/{id}.json'

def get_seed_data_path(seed: str):
    return f'./data/raw/seeds/{seed}.json'

def get_user_summary_path(username: str):
    return f'./data/processed/users/{username}.csv'

def get_game_summary_path(id: int):
    return f'./data/processed/games/{id}.csv'

def get_variant_winrate_path(id: int):
    return f'./data/processed/variants/winrates/{id}.csv'

def get_seed_summary_path(seed: str):
    return f'./data/processed/seeds/{seed}.csv'

def game_data_exists(id: int):
    gamepath = get_game_data_path(id)
    return _file_exists(gamepath)

def seed_data_exists(seed: str):
    seedpath = get_seed_data_path(seed)
    return _file_exists(seedpath)

def _file_exists(filepath: str):
    if path.isfile(filepath):
        return True
    return False

