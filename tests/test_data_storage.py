"""Tests data storage to ensure unique and chronological data"""

from hanabdata.tools.io import read

def test_user_data_redundancy_and_order():
    """Checks data is sorted chronologically, and no games are stored twice"""
    user_data = read.read_user('sodiumdebt')
    last_id = None
    for game_data in user_data:
        game_id = game_data["id"]
        if last_id is not None:
            assert game_id < last_id

def test_game_storage_spots():
    """tests that games are stored in chunks correctly"""
    chunk = 775
    games_data = read.read_chunk(chunk)
    for i, game in enumerate(games_data):
        if game is None:
            continue
        supposed_id = chunk * 1000 + i
        real_id = game["id"]
        assert supposed_id == real_id
    
def test_game_retrieval():
    """tests that asking for a game's data gives data for that game"""
    for game_id in range(776800, 777200):
        game = read.read_game_from_chunk(game_id)
        if game is None:
            continue
        assert game_id == game["id"]
