"""Iterates through all available metadata in preprocessed/games."""

from datetime import datetime
from hanabdata.tools.rating import Leaderboard
from hanabdata.tools.io.read import GamesIterator, write_ratings
from hanabdata.tools.restriction import STANDARD_GAME_RESTRICTION, has_winning_score

def get_ratings(restriction=STANDARD_GAME_RESTRICTION):
    """Implements this module."""
    lb = Leaderboard(draw_probability=0.0)
    gi = GamesIterator()

    current = datetime.now()
    for i, game in enumerate(gi):
        if not restriction.validate(game):
            continue
        v = (game["options"]["variantName"], game["options"]["numPlayers"])
        players = game["playerNames"]

        if has_winning_score(game):
            lb.update_and_rate(v, players, won=True)
        else:
            lb.update_and_rate(v, players, won=False)

        # if i > 1000:
        #     break

        if (datetime.now() - current).total_seconds() > 20:
            print(f"Finished updating ratings for {i} games.")
            current = datetime.now()

    # TODO: Neaten up output into something actually usable.
    write_ratings("users", lb.get_users())
    write_ratings("variants", lb.get_variants())

def print_ratings():
    """Outputs stuff to CLI."""
    print(get_ratings())

if __name__ == "__main__":
    print_ratings()