"""Maximum likelihood estimate for Hanabi.

Code attributed to https://github.com/naomiburks/collaborative_losses
"""

import numpy as np
from scipy.optimize import minimize, Bounds
from scipy.stats import beta
from hanabdata.tools.restriction import get_standard_restrictions, has_winning_score
from hanabdata.tools.io.read import write_csv
from hanabdata.tools.structures import  GamesIterator


PLAYER_NAMES = ["asael","asiaticlioness","BotScott","burger_king","LeCoco",\
    "EleNoClues","eliclax_PHL","Fafhrd","Feich,gw12346-league","hak",\
    "LeagueLana","hnter02","Inseres_2312l","jieship_league","nox",\
    "Kowalski1337_L","macanekLeague","MarkusKarlsen","Neempasta","HardTaffy",\
    "NishaNovar","karpov_league","olevino","Cinnamoroll","orucsLEAGUE",\
    "dapperblook","posij119","pro_joe","CoQuentinoo","rahsosprout","Ramanujan",\
    "ricardodd2","masteradept","rzL","sagnik1saha","zerodium","aspiring",\
    "KildaLeague","leagueknacker","Draku","TwinHoodie","vEnhanceLeague",\
    "vermling","hinomizu","FlameWill","obiwan_kenobi","youisme-ranked",\
    "sydneyf2","warrenleague","Leaguester","maxey","joano580","ReagerSe",\
    "benzloebleague","percolate","sagniksaha","LeagueGuyJCI","aaraleague",\
    "amattias"]


def get_win_odds(player_weaknesses, players):

    win_odds = 1
    for player in players:
        weakness = player_weaknesses[player]
        win_odds = win_odds * (1 - weakness)
    return win_odds


def get_log_likelihood(player_weaknesses, gamedata, prior_params):
    prior = get_prior_surprise(player_weaknesses, prior_params)
    log_likelihood = 0
    for game in gamedata:
        players = game["playerNames"]
        win_odds = get_win_odds(player_weaknesses, players)
        win = has_winning_score(game)
        if win:
            log_likelihood -= np.log(win_odds)
        else:
            log_likelihood -= np.log(1 - win_odds)
    return log_likelihood + prior

def get_prior_surprise(player_weaknesses, prior_params):
    surprise = 0
    for weakness in player_weaknesses.values():
        surprise = surprise - np.log(beta.pdf(weakness, prior_params[0], prior_params[1]))
    return surprise

def find_weaknesses(data, players, prior_params, initial_guess = None):
    if initial_guess is None:
        initial_guess = np.array([0.5 for _ in players])
    bounds = Bounds(lb=0.000001, ub=0.99999, keep_feasible=True)

    def get_odds(guess_list):
        player_weaknesses = {}
        for player, guess in zip(players, guess_list):
            player_weaknesses[player] = guess
        return get_log_likelihood(player_weaknesses, data, prior_params)

    result = minimize(get_odds, initial_guess, bounds=bounds)

    ratings = {}
    for player, weakness in zip(players, result.x): 
        ratings[player] = weakness
    return ratings


def find_prior(weaknesses, initial_guess = None):
    def get_surprise(params):
        surprise = 0
        for weakness in weaknesses:
            surprise = surprise - np.log(beta.pdf(weakness, params[0], 2.5 - params[0]))
        return surprise
    if initial_guess is None:
        initial_guess = np.array([2])
    bounds = Bounds(lb=1.00001, ub=2.99999, keep_feasible=True)
    optimized_prior = minimize(get_surprise, initial_guess, bounds=bounds).x
    return optimized_prior


def get_results(data, stop_at):
    game_counts = {}
    limited_data = []
    for game in data:
        if stop_at == 0:
            break
        for player in game["playerNames"]:
            if player not in game_counts:
                game_counts[player] = 0
            game_counts[player] += 1

        limited_data.append(game)
        stop_at -= 1

    players = sorted(game_counts.keys(), key=lambda player:game_counts[player], reverse=True)

    print(players)
    print(len(players), len(limited_data))

    result = find_weaknesses(limited_data, players, prior_params)
    for player in players:
        num_games = game_counts[player]
        if num_games == 1:
            plural = ''
        else:
            plural = 's'
        print(f"{player}: {np.round(100 * result[player], 1)}% with {num_games} game{plural} played.")

if __name__ == "__main__":
    prior_params = [1.1, 1.5]

    gi = GamesIterator()
    res = get_standard_restrictions()
    del(res.necessary_constraints["numTurns"])

    filtered_data = []
    for game in gi:
        if not res.validate(game):
            continue
        if game["id"] < 1083000:
            continue
        if game["options"]["numPlayers"] not in {3, 4, 5}:
            continue
        all_good_players = True
        for player in game["playerNames"]:
            if player not in PLAYER_NAMES:
                all_good_players = False
                break
        if not all_good_players:
            continue

        # if "MarkusKarlsen" in game["playerNames"]:
        #     print(game["id"])

        filtered_data.append(game)

        num_players = game["options"]["numPlayers"]
        curr_variant = game["options"]["variantName"] + f' {num_players}p'
        game["playerNames"].append(curr_variant)

    get_results(filtered_data, 30)
