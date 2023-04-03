"""Updates all user's score hunt files for currently downloaded games,
then creates a CSV report of each user's overall stats.
"""

import pathlib
from hanabdata.score_hunt import analyze_2P_score_hunt
from hanabdata.tools.io.read import get_score_hunt, write_score_hunt_summary

users_folder = pathlib.Path("./data/raw/users")

def get_users():
    """Returns a list of usernames."""
    user_list = []
    for user_file in users_folder.glob("*.json"):
        user_list.append(user_file.name[:-5])
    return user_list

def generate_score_hunt_report():
    """Takes average for each user in score hunt. Creates CSV."""
    users = get_users()
    hunts = [["player",
        "num variants",
        "avg duration",
        "avg attempts"
    ]]
    for user in users:
        hunts.append(_report_helper(user))
    write_score_hunt_summary(hunts)

def _report_helper(user):
    """Finds the averages """
    # makes sure data exists
    while True:
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


if __name__ == '__main__':
    generate_score_hunt_report()
