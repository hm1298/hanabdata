"""
This module contains functions for working with the file structure 
so that other modules don't have to both with it. Functions are self-explanatory enough that 
we disable the function docstring check from pylint.  
"""

# pylint: disable=missing-function-docstring
from os import path


def get_user_data_path(username: str):
    return f'./data/raw/users/{username}.json'


def get_game_data_path(game_id: int):
    return f'./data/raw/games/{game_id}.json'


def get_seed_data_path(seed: str):
    return f'./data/raw/seeds/{seed}.json'


def get_user_summary_path(username: str):
    return f'./data/processed/users/{username}.csv'


def get_game_summary_path(game_id: int):
    return f'./data/processed/games/{game_id}.csv'


def get_variant_winrate_path(variant_id: int):
    return f'./data/processed/variants/winrates/{variant_id}.csv'


def get_seed_summary_path(seed: str):
    return f'./data/processed/seeds/{seed}.csv'


def game_data_exists(game_id: int):
    gamepath = get_game_data_path(game_id)
    return _file_exists(gamepath)


def seed_data_exists(seed: str):
    seedpath = get_seed_data_path(seed)
    return _file_exists(seedpath)


def _file_exists(filepath: str):
    return path.isfile(filepath)
