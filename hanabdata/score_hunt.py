import datetime
from hanabdata.tools.restriction import STANDARD_2P, has_winning_score
from hanabdata.tools.io.read import read_user, write_score_hunt


def analyze_2P_score_hunt(username: str):
    """Reasons this is bad:
    - makes a dictionary for JSON first, then converts to csv afterwards (unnecessary)
    """

    data = read_user(username)

    score_hunt = {}
    # we cycle through in forwards chronological order
    for game in reversed(data):
        if not STANDARD_2P.validate(game):
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
            score_hunt[variant_id] = {
                'name': variant,
                'max_score': score, 
                'won': win, 
                'duration': duration,
                'attempts': 1,
            }
        else: 
            if score_hunt[variant_id]['won']:
                continue
            score_hunt[variant_id]['max_score'] = max(score_hunt[variant_id]['max_score'], score)
            score_hunt[variant_id]['won'] = win
            score_hunt[variant_id]['duration'] = score_hunt[variant_id]['duration'] + duration
            score_hunt[variant_id]['attempts'] = score_hunt[variant_id]['attempts'] + 1

    table = [['variant', 'max score', 'won', 'duration', 'attempts']]
    for info in score_hunt.values():
        table.append([info['name'], info['max_score'], info['won'], info['duration'], info['attempts']])
    write_score_hunt(username, table)

def analyze_2P_score_hunt2(username: str):
    """A function that creates the CSV in the original for loop."""

    data = read_user(username)

    table = [['variant', 'max score', 'won', 'duration', 'attempts']]
    score_hunt = {}
    # we cycle through in forwards chronological order
    for game in reversed(data):
        if not STANDARD_2P.validate(game):
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
            if line[2]:  # checks if already won
                continue
            line[1] = max(line[1], score)  # updates max score
            line[2] = win  # updates to True if necessary
            line[3] += duration  # adds to duration
            line[4] += 1  # adds to attempts

    write_score_hunt(username, table)

def analyze_2P_score_hunt3(username: str):
    """A function that creates the CSV in the original for loop."""

    data = read_user(username)

    table = [['variant', 'max score', 'won', 'duration', 'attempts']]
    table += [None] * 2300
    for game in reversed(data):
        if not STANDARD_2P.validate(game):
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

        line = table[variant_id + 1]
        if not line:
            table[variant_id + 1] = [variant, score, win, duration, 1]
        else:
            if line[2]:  # checks if already won
                continue
            line[1] = max(line[1], score)  # updates max score
            line[2] = win  # updates to True if necessary
            line[3] += duration  # adds to duration
            line[4] += 1  # adds to attempts

    ans_table = []
    for line in table:
        if line:
            ans_table.append(line)

    write_score_hunt(username, ans_table)


if __name__ == '__main__':
    username = input('username: ')
    analyze_2P_score_hunt3(username)