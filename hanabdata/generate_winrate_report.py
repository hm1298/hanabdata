"""Generates winrate report.

Writes to src/data/processed/variants/winrates/<file>.
"""

from hanabdata.tools.parse import generate_success_rate_summary
import hanabdata.tools.restriction as r
from hanabdata.tools.io.update import update_seed
from hanabdata.tools.io.read import seed_data_exists

def generate_success_rate_report(seed_prefix, limit, restriction, goal):
    """Writes to a CSV the success rate of a given goal among all games
    satisfying the given restriction for each of the first n seeds in a
    variant with given seed_prefix.
    """
    seeds, needs_update = [], []
    for i in range(1, limit + 1):
        seed = seed_prefix + str(i)
        seeds.append(seed)
        if not seed_data_exists(seed):
            needs_update.append(i)

    print(f'Missing data for {len(needs_update)} seeds. Adding now.')

    for i in needs_update:
        seed = seed_prefix + str(i)
        update_seed(seed)

    generate_success_rate_summary(seeds, restriction, goal)

N = 191
print(f'Finding the winrate among the first {N} No Variant games.')
generate_success_rate_report("p2v0s", N, r.STANDARD_GAME_RESTRICTION, \
   r.MAX_SCORE_ONLY)
