"""Looks for missing data, and fetches."""

from hanabdata.tools.structures import GamesIterator

def download_missing_games(game_id: int, skip_error=True):
    """Downloads all missing games with ID from 0 to game_id."""
    return