"""Prompts user for seed and generates report."""

from tools.update import update_seed
from tools.read import read_seed, write_seed_summary
from tools.paths import seed_data_exists
from tools.parse import get_noncheating_options


def generate_seed_report(seed : str):
    """Checks if JSON has been downloaded, then creates CSV."""
    if not seed_data_exists(seed):
        print('No seed data stored.')
        update_seed(seed)
    if not seed_data_exists(seed):
        return

    print('Seed data accessed. Processing...')
    data = read_seed(seed)

    parsed_seed_data = [[
        'game_id', 'score', 'turn_count', 'player_names', 'cheated',
        'speedrun', 'timed', 'link'
    ]]
    noncheating_options = get_noncheating_options()
    for game in data:
        options = game["options"]

        cheated = False
        for key in options:
            if key in noncheating_options:
                if options[key] != noncheating_options[key]:
                    cheated = True

        game_data = [
            game["id"], game["score"], game["numTurns"], game["playerNames"],
            cheated, options["speedrun"], options["timed"],
            f'https://hanab.live/replay/{game["id"]}'
        ]
        parsed_seed_data.append(game_data)

    write_seed_summary(seed, summary = parsed_seed_data)
    print('Successfully completed')

if __name__ == '__main__':
    generate_seed_report(input('enter seed: '))
    