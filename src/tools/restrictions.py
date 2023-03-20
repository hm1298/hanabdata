# still needs more thorough testing !!

# Creates a class to deal with various constraints that would be
# helpful to deal with large JSONs/dicts that need to be filtered in a
# variety of ways. In particular, can handle dicts stored in a dict (but
# not nested more than that), and can distinguish between requirements
# and optional features for data that has been processed at different
# points in time.

_EQUALITY_FUNCTION = lambda x, y: x == y
"""_CONSTANT_FUNCTION = lambda y: lambda x: y"""


# This should be refactored to allow for arbitrarily nested dicts (ew!)
# eventually. Requiring that Restriction.necessary and .optional only
# contain values that are of type Restriction or non-dict types like
# bool, int, string, maybe list? In other words, we can deal with the
# problem of nested dictionaries more cleanly by recursing through
# Restriction objects.
class Restriction:

	def __init__(self, necessary, optional):
		# Initialize all class variables
		self.necessary_constraints = necessary
		self._prune_duplicates(optional)
		self.optional_constraints = optional
		self.special_cases = {}

	def _prune_duplicates(self, dct):
		for key in self.necessary_constraints:
			if key in dct:
				del dct[key]

	"""def _dedictify(self, option, func, target):
		if type(option) == dict:
			if option not in target:
				target = {}
			for key in option:
				func(option, key, target)
		else:
			func"""

	def _evaluate(self, option, key=None):
		if option not in self.special_cases:
			return _EQUALITY_FUNCTION
		if key == None:
			return self.special_cases[option]
		if key not in self.special_cases[option]:
			return _EQUALITY_FUNCTION
		return self.special_cases[option][key]

	def add_special_case(self, option, func):
		if type(option) == dict:
			if option in self.special_cases:
				self.special_cases[option] = {}
			for key in option:
				self.special_cases[option][key] = func
		else:
			self.special_cases[option] = func

	def add_less_than(self, option):
		def func(x, y): return x < y
		self.add_special_case(option, func)

	def add_greater_than(self, option):
		def func(x, y): return x > y
		self.add_special_case(option, func)

	def validate(self, data):
		# print(data)
		for option in self.necessary_constraints:
			if option not in data:
				# print(f'gotcha, {option}')
				return False
			data_options = data[option]
			if type(data_options) != dict:
				value = self.necessary_constraints[option]
				# print(option)
				# print(data_options)
				# print(value)
				# print(self.special_cases)
				# print(self._evaluate(option)(data_options, value))
				if self._evaluate(option)(data_options, value):
					# print(f'gotcha2, {option}')
					continue
				return False
			for key in self.necessary_constraints[option]:
				if key not in data_options:
					# print(f'gotcha3, {option} {key}')
					return False
				value = self.necessary_constraints[option][key]
				# print(self._evaluate(option, key)(value, data[option][key]))
				if self._evaluate(option, key)(value, data[option][key]):
					# print(f'gotcha4, {option} {key}')
					continue
				return False

		# beware of errors in the following. changed the above and not
		# this yet (but it currently is not used by anything)
		for option in self.optional_constraints:
			if option not in data:
				continue
			if type(option) != dict:
				value = self.necessary_constraints[option]
				if data[option] != self._evaluate(option)(value):
					return False
				continue
			for key in option:
				if key not in data[option]:
					continue
				value = self.necessary_constraints[option][key]
				if data[option][key] != self._evaluate(option, key)(value):
					return False

		return True


def get_standard_restrictions(): 
	only_good_games = {
		"options": {
			"startingPlayer": 0,  
	        "cardCycle" : False, 
	        "deckPlays" : False, 
	        "emptyClues" : False, 
	        "oneExtraCard" : False,
	        "oneLessCard" : False,
	        "allOrNothing" : False,
	        "detrimentalCharacters" : False,
	        "speedrun": False,
		},
		"numTurns": 3
	}
	# WARNING: I'm not sure where numTurns vs turn_count is used, so
	# this may not be compatible over different formats. In that case,
	# such checks may be safely moved to optional if data processing may
	# change the name of this key.

	standard = Restriction(only_good_games, {"cheated": False})
	standard.add_greater_than("numTurns")

	return standard

STANDARD_GAME_RESTRICTION = get_standard_restrictions()
MAX_SCORE_ONLY = Restriction({"score": 25}, {})
