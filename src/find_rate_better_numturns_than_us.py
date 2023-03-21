"""to be deleted or whatever but serves as an example for now"""

from generate_seed_report import generate_seed_report
from tools.parse import generate_success_rate_summary
from tools.restriction import Restriction
from tools.restriction import MAX_SCORE30_ONLY

SEED = "p2v3s3"
TURN_COUNT = 77

faster_than_us = Restriction({"numTurns": TURN_COUNT}, {})
faster_than_us.add_less_than("numTurns")

generate_seed_report(SEED)

generate_success_rate_summary([SEED], MAX_SCORE30_ONLY, faster_than_us)
