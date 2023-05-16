"""Updates all user's score hunt files for currently downloaded games,
then creates a CSV report of each user's overall stats.
"""

from hanabdata.score_hunt import analyze_2P_score_hunt, ScoreHunt
from hanabdata.tools.restriction import get_standard_restrictions
from hanabdata.tools.io.read import get_score_hunt, get_users, \
    write_score_hunt_summary, read_user

def generate_score_hunt_report():
    """Takes average for each user in score hunt. Creates CSV."""
    users = get_users()
    hunts = [["player",
        "num variants",
        "avg duration",
        "avg attempts"
    ]]
    for user in users:
        hunts.append(_report_helper(user, new_report=True))
    write_score_hunt_summary(hunts)

def _report_helper(user, new_report=False, data=None):
    """Finds the averages """
    # makes sure data exists
    while not data:
        if new_report:
            analyze_2P_score_hunt(user)
        data = get_score_hunt(user)
        if data is None:
            analyze_2P_score_hunt(user)
            continue
        break

    num_variants, avg_duration, avg_attempts = 0, 0, 0
    hunt_iter = iter(data)
    next(hunt_iter)

    # checks all games in data and creates statistics
    for game_summary in hunt_iter:
        if not bool(game_summary[2]):
            continue
        num_variants += 1
        avg_duration += float(game_summary[3])
        avg_attempts += int(game_summary[4])

    if num_variants == 0:
        avg_duration = 999999
        avg_attempts = 999999
    else:
        # converts avg_duration to minutes
        avg_duration /= (num_variants * 60)
        avg_attempts /= num_variants
    return [user, num_variants, avg_duration, avg_attempts]

def score_hunt_for_teams():
    """Hi."""
    teams = set()
    users = get_users()
    # score_hunts = {user: get_score_hunt(user) for user in users}
    print("Got score hunts")
    for user in users:
        data = read_user(user)
        teammates = {}
        for game in data:
            for player in game["playerNames"]:
                if player == user or game["options"]["numPlayers"] != 2:
                    continue
                if player not in teammates:
                    teammates[player] = 1
                else:
                    teammates[player] += 1
        for player, num_games in teammates.items():
            if num_games >= 17:
                teams.add(alphabetize(user, player))

    hunts = [["team",
        "num variants",
        "avg duration",
        "avg attempts"
    ]]
    print(f"Starting teams. {len(teams)} to go..")
    for team in teams:
        restriction = get_standard_restrictions(2)
        restriction.add_filter("playerNames", team[1])
        restriction.add_contains("playerNames")

        def dummy_func(x, y, z): return x + y + z
        sh = ScoreHunt(dummy_func)
        sh.set_filter(restriction)
        try:
            sh.add_data(reversed(read_user(team[0])))
        except FileNotFoundError:
            print(f"Couldn't find user {team[0]}. Omitting team {team} and continuing..")
            continue
        table = sh.analyze()

        # for index, line in enumerate(table):
        #     if index == 0:
        #         continue
        #     if not_first_win(int(line[2]), line[0], score_hunts[team[0]], score_hunts[team[1]]):
        #         table.pop(index)

        hunts.append(_report_helper(team, data=table))
    write_score_hunt_summary(hunts)

def not_first_win(game_id, variant, score_hunt1, score_hunt2):
    """Returns True or False."""
    answer1, answer2 = False, False
    for line in score_hunt1:
        if line[0] == variant:
            print(line[2])
            if line[2] and game_id > int(line[2]):
                answer1 = True
                break
    for line in score_hunt2:
        if line[0] == variant:
            if game_id > line[2]:
                answer2 = True
                break
    return answer1 and answer2

def alphabetize(player1, player2):
    """Returns ordered tuple."""
    if player1 > player2:
        return player2, player1
    return player1, player2

if __name__ == '__main__':
    score_hunt_for_teams()
