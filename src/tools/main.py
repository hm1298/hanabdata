from tools.parse import GameData, generate_user_summary, get_seed_winrate, generate_winrate_summary
from tools import read


generate_winrate_summary()

"""
username = 'sodiumdebt'
generate_user_summary(username)



id = 326178
data = read.read_game(id)

parser = GameData(data)
summary = parser.generate_line_summary()
print(summary)
"""