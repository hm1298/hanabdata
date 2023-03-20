from tools.update import update_seed
from tools.read import read_seed, write_seed_summary
from tools.paths import seed_data_exists
from tools.parse import get_noncheating_options

def generate_winrate_report(seedPrefix : str, n : int, allowCheaters=False):
	noncheating_options = get_noncheating_options()

	needsUpdate = []
	for i in range(1, n + 1):
		seed = seedPrefix + str(i)
		if not seed_data_exists(seed):
			needsUpdate.append(i)

	print(f'Missing data for {len(needsUpdate)} seeds. Adding now.')

	for i in needsUpdate:
		seed = seedPrefix + str(i)
		update_seed(seed)

generate_winrate_report("p2v0s", 191)