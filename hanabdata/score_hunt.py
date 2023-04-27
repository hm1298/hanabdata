"""Determines number of attempts and total duration of play time
leading up to a player's first win in each variant. Prints to a CSV in
data/processed/score_hunts.
"""

import datetime
from hanabdata.tools.restriction import STANDARD_2P, has_winning_score
from hanabdata.tools.io.read import read_user, write_score_hunt


def analyze_2P_score_hunt(username: str, restriction=STANDARD_2P):
    """A function that creates the CSV in the original for loop."""

    data = read_user(username)

    # table stores the information for the CSV writer, and score_hunt
    # stores the table indices for each variant
    table = [['variant', 'max score', 'won', 'duration', 'attempts']]
    score_hunt = {}
    # we cycle through in forwards chronological order
    for game in reversed(data):
        if not restriction.validate(game):
            # note: the standard restriction throws out games with less
            # than 3 turns. this may boost some player's numbers to an
            # unfair extent, depending on scorehunting strategy
            continue
        variant = game['options']['variantName']
        variant_id = game['options']['variantID']
        start_time = datetime.datetime.fromisoformat(game['datetimeStarted'])
        end_time = datetime.datetime.fromisoformat(game['datetimeFinished'])
        score = game['score']
        duration = (end_time - start_time).total_seconds()
        win = has_winning_score(game)

        if variant_id not in score_hunt:
            score_hunt[variant_id] = len(table)
            table.append([variant, score, win, duration, 1])
        else:
            line = table[score_hunt[variant_id]]
            if line[2]:
                continue
            # updates max score
            line[1] = max(line[1], score)
            # updates win status to True if necessary
            line[2] = win
            # adds to duration & attempts
            line[3] += duration
            line[4] += 1

    write_score_hunt(username, table)


if __name__ == '__main__':
    username = input('username: ')
    analyze_2P_score_hunt(username)
