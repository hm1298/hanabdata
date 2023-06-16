"""Iterates through all available metadata in preprocessed/games."""

from datetime import datetime
from hanabdata.process_games import get_players_with_x_games
from hanabdata.tools.rating import LBSoloEnvironment, get_average_of_column
from hanabdata.tools.io.read import GamesIterator, write_ratings, _read_csv
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score

NUM_PLAYERS = 4
# for 3p,
# SUGGESTED_MU = 33.601927130816925
# for 4p,
SUGGESTED_MU = 36.3
# for 5p,
# SUGGESTED_MU = 47.5

def get_ratings(avg=73.6, restriction=get_standard_restrictions(NUM_PLAYERS), run=1):
    """Implements this module."""
    lb = LBSoloEnvironment(draw_probability=0.0)
    file_infix = f"_{NUM_PLAYERS}p_iter"
    lb.set_variant_rating(avg, modify_beta=True)
    try:
        lb.set_variants(_read_csv(f"./data/processed/ratings/variants{file_infix}{run}.csv"))
    except FileNotFoundError:
        print(f"No file found on run {run}.")
    gi = GamesIterator(oldest_to_newest=True)

    current = datetime.now()
    # valid_games, total_wins = 0, 0
    # num_games_played = {}
    # valid_players = get_players_with_x_games(100)
    for i, game in enumerate(gi):
        if not restriction.validate(game):
            continue
        # if game["options"]["numPlayers"] == 2:
        #     continue
        v = (game["options"]["variantName"], game["options"]["numPlayers"])
        players = game["playerNames"]
        # valid_games += 1

        # good = True
        # for player in players:
        #     # num_games_played[player] = num_games_played.get(player, 0) + 1
        #     if player not in valid_players:
        #         good = False
        #         break

        # if not good:
        #     continue

        # print("currently on:", v, players)

        if has_winning_score(game):
            # total_wins += 1
            lb.update_and_rate(v, players, won=True, update_var=True)
        else:
            lb.update_and_rate(v, players, won=False, update_var=True)

        # if i > 100000:
        #     break

        if (datetime.now() - current).total_seconds() > 20:
            print(f"Finished updating ratings for {i} games.")
            current = datetime.now()

    # print(f"Total winrate is {total_wins / valid_games}.")
    print(f"Saved ratings with variant mu = {avg} to file.")

    write_ratings(f"users{file_infix}{run+1}", lb.get_users())
    write_ratings(f"variants{file_infix}{run+1}", lb.get_variants())
    return lb.get_variants(), lb.get_users()

def print_ratings():
    """Outputs stuff to CLI."""
    print(get_ratings())

def find_appropriate_defaults(how_long: int, step_weight=1.99, margin_of_error=0.1, search=True):
    """Searches for an appropriate default lb.variant_mu value."""
    current_error, current_avg, i = 100.0, SUGGESTED_MU, 0
    while i < how_long:
        variant_table, _ = get_ratings(avg=current_avg, run=i)
        current_avg = get_average_of_column(variant_table, 3)
        # current_error = current_avg - mu
        # if abs(current_error) < margin_of_error:
        #     break
        # print(f"Updating {mu:.4f} because result {current_avg:.4f} is too far away.")
        # mu += step_weight * current_error
        i += 1
    return current_avg

if __name__ == "__main__":
    print(find_appropriate_defaults(10, search=False))
