#to be deleted or whatever but I wanted to test a different case of rate

from generate_seed_report import generate_seed_report
from tools.parse import generate_success_rate_summary
from tools.restriction import Restriction
from tools.restriction import STANDARD_GAME_RESTRICTION, MAX_SCORE_ONLY

SEED = "p2v3s3"
TURN_COUNT = 77

better_numturns_than_us = Restriction({"numTurns": TURN_COUNT}, {})
better_numturns_than_us.add_less_than("numTurns")

generate_seed_report(SEED)

generate_success_rate_summary([SEED], better_numturns_than_us, MAX_SCORE_ONLY)