"""Downloads games."""

from hanabdata.tools.io.update import update_game, update_chunk

def download(game_id: int):
    """Downloads game."""
    update_game(game_id)

def download_all(game_id: int):
    """Downloads all games starting from game_id."""
    chunk = game_id // 1000
    while True:
        update_chunk(chunk)
        chunk += 1

if __name__ == '__main__':
    download_all(1)
