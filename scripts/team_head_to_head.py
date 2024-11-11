"""Creates a scorecard for team 1 vs team 2."""

import hanabdata.tools.restriction as res
from hanabdata.tools.io.read import write_csv
from hanabdata.tools.structures import User

def compare_teams(team1: list, team2: list, size=None, save=True, restriction=None):
    """Compares teams."""
    team1.sort()
    team2.sort()
    if size is None:
        size = len(team2)
    if restriction is None:
        restriction = res.get_standard_restrictions(size)
    if len(team1) != len(team2):
        return
    games = {}
    for game in User.load(team1[0]):
        if not restriction.validate(game):
            continue
        if team1 != sorted(game["playerNames"]):
            continue
        if game["seed"] == "JSON":
            continue
        games[game["seed"]] = game
    valid_games = {}
    for game in User.load(team2[0]):
        if not restriction.validate(game):
            continue
        if team2 != sorted(game["playerNames"]):
            continue
        if game["seed"] == "JSON":
            continue
        if game["seed"] in games:
            valid_games[game["seed"]] = [games[game["seed"]], game]
    print(f"{len(valid_games)} games found.")
    info = {"team1": team1, "team2": team2}
    for _, entry in valid_games.items():
        score = award_points(entry[0], entry[1])
        variant = entry[0]["options"]["variantName"]
        info.setdefault(variant, [0, 0])
        if score == 0:
            continue
        if score < 0:
            info[variant][1] -= score
        else:
            info[variant][0] += score
    if save:
        save_to_file(info)
    return info

def compare_players(player1: str, player2: str, size=None, save=True, restriction=None):
    """Compares players."""
    if size is None:
        size = 2
    if restriction is None:
        restriction = res.get_standard_restrictions(size)
    games = {}
    for game in User.load(player1):
        if not restriction.validate(game):
            continue
        if game["seed"] == "JSON":
            continue
        games[game["seed"]] = game
    valid_games = {}
    for game in User.load(player2):
        if not restriction.validate(game):
            continue
        if game["seed"] == "JSON":
            continue
        if game["seed"] in games:
            valid_games[game["seed"]] = [games[game["seed"]], game]
    print(f"{len(valid_games)} games found.")
    info = {"team1": player1, "team2": player2}
    for _, entry in valid_games.items():
        score = award_points(entry[0], entry[1])
        variant = entry[0]["options"]["variantName"]
        info.setdefault(variant, [0, 0])
        if score == 0:
            continue
        if score < 0:
            info[variant][1] -= score
        else:
            info[variant][0] += score
    if save:
        save_to_file(info)
    return info

def award_points(game1, game2):
    """Determines who played the game better.
    3 points for win over loss; 1 point for merely higher score.
    """
    score1, score2 = game1["score"], game2["score"]
    if score1 == score2:
        return 0
    win1, win2 = res.has_winning_score(game1), res.has_winning_score(game2)
    if win1:
        return 3
    if win2:
        return -3
    if score1 > score2:
        return 1
    return -1

def save_to_file(info):
    """Saves to file."""
    name1 = "".join(s[:2] for s in info.pop("team1"))
    name2 = "".join(s[:2] for s in info.pop("team2"))
    if info == {}:
        return
    file_path = f'./data/processed/matchpoints/{name1}_{name2}.csv'
    header = ["Variant", name1, name2]
    header2 = ["TOTAL", 0, 0]
    table = [header, header2]
    for variant, matchpoints in info.items():
        table.append([variant, matchpoints[0], matchpoints[1]])
        header2[1] += matchpoints[0]
        header2[2] += matchpoints[1]
    write_csv(file_path, table)

if __name__ == "__main__":
    compare_teams(["hallmark", "sodiumdebt"], ["mgold", "yagami_black"])
    compare_players("gsymon", "hallmark")