from tools.update import update_seed
from tools.read import read_seed, write_seed_summary
from tools.paths import seed_data_exists
from tools.parse import get_noncheating_options


def generate_seed_report(seed : str):
    noncheating_options = get_noncheating_options()
    if not seed_data_exists(seed):
        print(f'No seed data stored.')
        update_seed(seed)
    if not seed_data_exists(seed):
        return
    
    print(f'Seed data accessed. Processing...')
    data = read_seed(seed)
    
    parsed_seed_data = [['game_id', 'score', 'turn_count', 'player_names', 'cheated', 'speedrun', 'timed', 'link']]
    for game in data:

        options = game["options"]
        cheated = True
        for key in options:
            if key in noncheating_options:
                if options[key] != noncheating_options[key]:
                    cheated = False
                    
        speedrun = options["speedrun"]
        timed = options["timed"]
        
        game_id = game["id"]
        score = game["score"]
        turn_count = game["numTurns"]
        player_names = game["playerNames"]
        link = f'hanab.live/replay/{game_id}'
        game_data = [game_id, score, turn_count, player_names, cheated, speedrun, timed, link]
        parsed_seed_data.append(game_data)

    write_seed_summary(seed, summary = parsed_seed_data)








if __name__ == '__main__':
    seed = input('enter seed: ')
    generate_seed_report(seed)
    