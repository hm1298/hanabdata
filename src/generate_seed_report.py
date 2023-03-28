"""Prompts user for seed and generates report."""

from tools.restriction import NONCHEATING_RESTRICTION
from tools.io.update import update_seed
from tools.io.read import read_seed, write_seed_summary, seed_data_exists


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
    for game in data:
        options = game["options"]

        cheated = NONCHEATING_RESTRICTION.validate(game)

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
    