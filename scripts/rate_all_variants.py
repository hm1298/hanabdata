"""Iterates through all available metadata in preprocessed/games."""

from datetime import datetime
from hanabdata.process_games import get_players_with_x_games
from hanabdata.tools.rating import Leaderboard
from hanabdata.tools.io.read import GamesIterator, write_ratings
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score

NUM_PLAYERS = 2

def get_ratings(restriction=get_standard_restrictions(NUM_PLAYERS)):
    """Implements this module."""
    lb = Leaderboard(draw_probability=0.0)
    gi = GamesIterator(oldest_to_newest=True)

    current = datetime.now()
    valid_games, total_wins = 0, 0
    # num_games_played = {}
    valid_players = get_players_with_x_games(100)
    for i, game in enumerate(gi):
        if not restriction.validate(game):
            continue
        v = (game["options"]["variantName"], game["options"]["numPlayers"])
        players = game["playerNames"]
        valid_games += 1

        good = True
        for player in players:
            # num_games_played[player] = num_games_played.get(player, 0) + 1
            if player not in valid_players:
                good = False
                break

        if not good:
            continue

        if has_winning_score(game):
            total_wins += 1
            lb.update_and_rate(v, players, won=True, update_var=good)
        else:
            lb.update_and_rate(v, players, won=False, update_var=good)

        # if i > 100000:
        #     break

        if (datetime.now() - current).total_seconds() > 20:
            print(f"Finished updating ratings for {i} games.")
            current = datetime.now()

    print(f"Total winrate is {total_wins / valid_games}.")

    # TODO: Neaten up output into something actually usable.
    write_ratings(f"users_{NUM_PLAYERS}p", lb.get_users())
    write_ratings(f"variants_{NUM_PLAYERS}p", lb.get_variants())
    # return lb.get_variants(), lb.get_users()

def print_ratings():
    """Outputs stuff to CLI."""
    print(get_ratings())

if __name__ == "__main__":
    print_ratings()