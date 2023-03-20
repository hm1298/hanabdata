from tools.update import update_seed
from tools.read import read_seed, write_seed_summary
from tools.paths import seed_data_exists
from tools.parse import get_noncheating_options
from tools.parse import generate_winrate_summary
from tools.restrictions import *

def generate_winrate_report(seedPrefix : str, n : int, restriction, winrate):
	noncheating_options = get_noncheating_options()

	seeds, needsUpdate = [], []
	for i in range(1, n + 1):
		seed = seedPrefix + str(i)
		seeds.append(seed)
		if not seed_data_exists(seed):
			needsUpdate.append(i)

	print(f'Missing data for {len(needsUpdate)} seeds. Adding now.')

	for i in needsUpdate:
		seed = seedPrefix + str(i)
		update_seed(seed)

	generate_winrate_summary(seeds, restriction, winrate)

print(STANDARD_GAME_RESTRICTION)
generate_winrate_report("p2v0s", 191, STANDARD_GAME_RESTRICTION, MAX_SCORE_ONLY)
