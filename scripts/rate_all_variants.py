"""Iterates through all available metadata in preprocessed/games."""

from datetime import datetime
from whr import whole_history_rating
from whr.utils import test_stability
from hanabdata.process_games import get_players_with_x_games
import hanabdata.tools.rating as rating
from hanabdata.tools.structures import GamesIterator
from hanabdata.tools.io.read import write_ratings, read_csv
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score

NUM_PLAYERS = 3
TEAM_SIZES = [2, 3, 4, 5, 6]
DAY_ZERO = datetime.fromisoformat("2018-01-18T01:53:29Z").date()
TRACKED_PLAYERS = ["spring", "yagami_black", "piper", "Lanvin", "HelanaAshryvr", "MarkusKahlsen", "TimeHoodie", "gabio"]
BLOCKED_PLAYERS = ["Carunty", "FrancisFok"]
UPDATE_IN_DAYS = 7
# for 2p,
# SUGGESTED_MU = 31.0
# for 3p,
SUGGESTED_MU = 33.6
# for 4p,
# SUGGESTED_MU = 36.3
# for 5p,
# SUGGESTED_MU = 47.5

def get_ratings(avg=SUGGESTED_MU, restriction=get_standard_restrictions(NUM_PLAYERS), run=1):
    """Implements this module."""
    lb = rating.LBSoloEnvironment(mu=avg)
    # lb = rating.MatchPointLB(draw_probability=0.8)
    file_infix = "_iter_new_2p_"
    # lb.set_variant_rating(avg, modify_beta=True)
    try:
        prev_file = f"./data/processed/ratings/variants{file_infix}{run}.csv"
        lb.set_variants(read_csv(prev_file))
    except FileNotFoundError:
        print(f"No file found on run {run}.")
    gi = GamesIterator(oldest_to_newest=True)

    current = datetime.now()
    # valid_games, total_wins = 0, 0
    # num_games_played = {}
    valid_players = get_players_with_x_games(100)
    for player in BLOCKED_PLAYERS:
        valid_players.pop(player, None)
    player_info = {player: [None] for player in TRACKED_PLAYERS}
    prev_date = datetime.fromisoformat("2018-01-01T01:00:00Z")
    for i, game in enumerate(gi):
        if not restriction.validate(game):
            continue
        # if game["options"]["numPlayers"] not in TEAM_SIZES:
        #     continue
        v = (game["options"]["variantName"], game["options"]["numPlayers"])
        players = game["playerNames"]
        # valid_games += 1

        good = True
        for player in players:
            # num_games_played[player] = num_games_played.get(player, 0) + 1
            if player not in valid_players:
                good = False
                break

        if not good:
            continue

        # print("currently on:", v, players)

        if has_winning_score(game):
            # total_wins += 1
            lb.update_and_rate(v, players, won=True)
        else:
            lb.update_and_rate(v, players, won=False)

        # if i > 100000:
        #     break

        try:
            curr_date = datetime.fromisoformat(game["datetimeFinished"])
        except KeyError as e:
            print(game)
            raise e
        if (curr_date - prev_date).days > UPDATE_IN_DAYS:
            prev_date = curr_date
            for player in TRACKED_PLAYERS:
                player_info[player].append(lb.get_player_ranking(player))

        if (datetime.now() - current).total_seconds() > 20:
            print(f"Finished updating ratings for {i} games.")
            current = datetime.now()

    # print(f"Total winrate is {total_wins / valid_games}.")
    print(f"Saved ratings with variant mu = {avg} to file.")

    write_ratings("tracked_players", [[player] + player_info[player] for player in TRACKED_PLAYERS])
    write_ratings(f"users{file_infix}{run+1}", lb.get_users())
    write_ratings(f"variants{file_infix}{run+1}", lb.get_variants())
    return lb.get_variants(), lb.get_users()

def print_ratings():
    """Outputs stuff to CLI."""
    print(get_ratings())

def find_appropriate_defaults(how_long: int, step_weight=1.8, margin_of_error=0.1, search=True):
    """Searches for an appropriate default lb.variant_mu value."""
    curr_error, curr_avg, i = 100.0, SUGGESTED_MU, 0
    mu = curr_avg
    while i < how_long:
        variant_table, _ = get_ratings(avg=curr_avg, run=i)
        curr_avg = rating.get_average_of_column(variant_table, 3)
        curr_error = curr_avg - mu
        if abs(curr_error) < margin_of_error:
            break
        print(f"Updating {mu:.4f} because result {curr_avg:.4f} is too far away.")
        mu += step_weight * curr_error
        i += 1
    return curr_avg

# TODO: put this in a module to help scripts/analyses in general
def get_player_games(restriction, min_games_played, min_games_to_rank=None):
    """Returns dictionary of players pointing to game info."""
    if min_games_to_rank is None:
        min_games_to_rank = min_games_played

    gi = GamesIterator(oldest_to_newest=False)
    valid_players = get_players_with_x_games(min_games_played)

    # filters out games that do not meet restriction or have all
    # players with at least min_games_played games played
    result, games_played = {}, {}
    for i, game in enumerate(gi):
        if not restriction.validate(game):
            continue

        v = f'{game["options"]["variantName"]} ({game["options"]["numPlayers"]} players)'
        players = game["playerNames"]
        day = datetime.fromisoformat(game['datetimeFinished']).date() - DAY_ZERO

        good = True
        for player in players:
            if player not in valid_players:
                good = False
                break
        if not good:
            continue

        entry = [v, players, has_winning_score(game), day]
        for player in players:
            games_played[player] = games_played.get(player, 0) + 1
            result.setdefault(player, [])
            result[player].append(entry)

        # if i > 100000:
        #     break

    # removes players who do not have sufficient number games after
    # passing through the filter
    for player, amt in games_played.items():
        if amt < min_games_to_rank:
            result.pop(player)

    return result

def whr_ratings(num_iterations=50, cutoff_time=120, restriction=get_standard_restrictions()):
    """Uses a different rating system."""
    lb = whole_history_rating.Base(config={"w2":14.0})
    restriction.add_filter("playerNames", 2)
    restriction.add_special_case("playerNames", lambda x, y: len(x) > y)
    game_lookup = get_player_games(restriction, 100)

    variant_names = set()
    for player, games in game_lookup.items():
        for game in games:
            [v, _, won, day] = game
            variant_names.add(v)

            win_indicator = "B"
            if won:
                win_indicator = "W"
            lb.create_game(v, player, win_indicator, day.days, 0)

    print("Starting iteration..")
    i = 0
    start = datetime.now()
    while True:
        lb.iterate(5)
        elapsed = (datetime.now() - start).total_seconds() / 60
        print(f"Completed 5 of new iteration. {elapsed:.4f} minutes total")
        lb.iterate(44)
        a = lb.get_ordered_ratings(compact=True)
        lb.iterate(1)
        b = lb.get_ordered_ratings(compact=True)

        save_rating_to_file(lb.get_ordered_ratings(current=True), variant_names)
        print("Trying to pickle..")
        try:
            # silly package seems unable to pickle
            lb.save_base("./data/processed/ratings/whr_base.pickle")
        except RecursionError:
            print("Unable to pickle.")

        i += 50
        elapsed = (datetime.now() - start).total_seconds() / 60
        print(f"Completed 50 of new iteration. {elapsed:.4f} minutes total")
        if test_stability(a, b, precision=1):
            if test_stability(a, b, precision=0.1):
                print("Reached stability of 0.1 !!!")
                if test_stability(a, b, precision=0.01):
                    print("AND 0.01 !!!")
                    break
            else:
                print("Reached stability of 1.0")

    return lb.get_ordered_ratings(current=True), variant_names

def save_whr(cutoff_time=120, run=3):
    """Saves whr."""
    ratings, var_set = whr_ratings(cutoff_time=cutoff_time)

    save_rating_to_file(ratings, var_set, run)

def save_rating_to_file(ratings, var_set, run=3):
    """Makes CSV and saves it."""
    variants_table = []
    users_table = []

    for rating in ratings:
        name, value = rating[0], rating[1]
        if name in var_set:
            variants_table.append([name, name[:-12], name[-10], value])
        else:
            users_table.append([name, value])

    variants_table.append(["Game Type", "Variant Name", "Num Players", "Rating"])
    users_table.append(["User", "Rating"])

    write_ratings(f"users_whr{run}", users_table[::-1])
    write_ratings(f"variants_whr{run}", variants_table[::-1])

if __name__ == "__main__":
    print(find_appropriate_defaults(4, search=False))
    # sys.setrecursionlimit(200000) <- causes Segmentation faults
    # save_whr(10 * 60 * 60)

# changed set_variants() to use sigma = mu / 3 rather than
# old sigma, and ending average mu changed from 33.6 over
# iterations to 34.97 in latest iteration. hmm.
