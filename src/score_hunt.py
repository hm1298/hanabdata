import datetime
from tools.read import read_user, write_score_hunt


def analyze_2P_score_hunt(username: str):
    """Reasons this is bad:
    - does not account for cheating options
    - makes a dictionary for JSON first, then converts to csv afterwards (unnecessary)
    - extraction of number of suits

    
    """

    data = read_user(username)
    
    score_hunt = {}
    # we cycle through in forwards chronological order
    for game in reversed(data):
        if game["options"]["numPlayers"] != 2:
            continue
        #game_id = game['id']
        variant = game['options']['variantName']
        variant_id = game['options']['variantID']
        start_time = datetime.datetime.fromisoformat(game['datetimeStarted'])
        end_time = datetime.datetime.fromisoformat(game['datetimeFinished'])
        score = game['score']
        duration = (end_time - start_time).total_seconds()

        suit_count = 5
        for char in variant:
            try:
                suit_count = int(char)
                break
            except ValueError:
                continue
        max_score = 5 * suit_count
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