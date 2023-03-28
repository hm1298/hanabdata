import datetime
from tools.restriction import STANDARD_2P
from game.variants import find_variant
from tools.io.read import read_user, write_score_hunt


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

        max_score = 5 * len(find_variant(variant_id).suits)
        win = (score == max_score)




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


if __name__ == '__main__':
    username = input('username: ')
    analyze_2P_score_hunt(username)