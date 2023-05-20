"""
This module contains functions for reading and writing data to the file structure 
so that other modules don't have to deal with it. Functions are self-explanatory enough that 
we disable the function docstring check from pylint.  
"""

# pylint: disable=missing-function-docstring
import csv
import json
import pathlib
from os import path
from .. import structures

def write(tag, data, data_type = 'user', processing_level = 'raw'):
    file_path = f'./data/{processing_level}/{data_type}s/{tag}'
    if processing_level == 'raw':
        file_path = file_path + '.json'
        write_json(file_path, data)
    else:
        file_path = file_path + '.csv'
        write_csv(file_path, data)

def get_file_names(path: str):
    """Returns a list of JSON files in the given directory."""
    file_list = []
    folder = pathlib.Path(path)
    for file in folder.glob("*.json"):
        file_list.append(file.name[:-5])
    return file_list



def read_games_from_chunk(games: list, chunk: int, meta=False):
    """Assumes games is sorted reverse chronologically.

    Also assumes all entries are >= the least ID in chunk.

    Returns a dict:
        keys - IDs from games, inserted in increasing order
        values - game data for matching ID from file (could be None)
    """
    if meta:
        chunk_path = f'./data/preprocessed/games/{chunk}'
    else:
        chunk_path = f'./data/raw/games/{chunk}'
    if file_exists(chunk_path):
        try:
            if meta:
                data = structures.ChunkMeta.load(chunk)
            else: 
                data = structures.Chunk.load(chunk)
        except ValueError:
            data = [None] * 1000
    else:
        data = [None] * 1000
    games_dict = {}
    while games and games[-1] < (chunk + 1) * 1000:
        game_id = games.pop()
        assert game_id >= chunk * 1000
        games_dict[game_id] = data[game_id % 1000]
    return games_dict

def write_games_to_chunk(games: dict, chunk: int, meta=False):
    # note file should exist if this function is called. checks anyway
    if meta:
        chunk_path = f'./data/preprocessed/games/{chunk}.json'
    else:
        chunk_path = f'data/raw/games/{chunk}.json'

    if file_exists(chunk_path):
        try:
            if meta:
                data = structures.ChunkMeta.load(chunk).data
            else: 
                data = structures.Chunk.load(chunk).data
        except ValueError:
            data = [None] * 1000
    else:
        data = [None] * 1000
    for game_id in games:
        _, i = divmod(game_id, 1000)
        assert _ == chunk  # remove
        data[i] = games[game_id]
    write_json(chunk_path, data)

def get_users():
    """Returns a list of usernames."""
    return get_file_names("./data/raw/users")

def get_game_ids():
    """Returns a list of game IDs from the old format."""
    return get_file_names("./data/raw/games")




def file_exists(filepath: str):
    return path.isfile(filepath)

# Read and write JSONs and CSVs

def read_json(file_path):
    with open(file_path, encoding="utf8") as json_file:
        try:
            data = json.load(json_file)
        except BaseException as e:
            print(e)
            print(f"The offending file is found at: {file_path}")
            raise e
    return data

def write_json(file_path, txt: str):
    with open(file_path, 'w', encoding="utf8") as outfile:
        json.dump(txt, outfile)

def read_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        return list(csvreader)

def write_csv(file_path, data: list):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(data)