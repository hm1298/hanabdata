"""temp

..
"""

import numpy as np
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

    result = [0]
    table = [["player name", "num games", "loss contribution"]]
    file_path = file_path = f'./data/league_mle/round_of_{len(limited_data)}.csv'
    for player in players:
        table.append([player, game_counts[player], np.round(100 * result[player], 6)])
    write_csv(file_path, table)
    return table, result

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

    master_table = get_results(filtered_data, len(filtered_data))[0]

    for i in range(len(filtered_data) - 1):
        if i < 235:
            continue
        if i % 20 == 0:
            partial_update = get_results(filtered_data, i+1)[1]
            for line in master_table:
                player = line[0]
                if player in partial_update:
                    line.append(np.round(100 * partial_update[player], 6))
                elif player == "player name":
                    j = i // 20 + 1
                    line.append(f"loss at step {j}")
                else:
                    line.append(0)
            write_csv("./data/league_mle/loss_over_time.csv", master_table)
