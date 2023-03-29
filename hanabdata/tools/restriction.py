"""Creates a class to deal with various constraints that would be
helpful to deal with large JSONs/dicts that need to be filtered in a
variety of ways. In particular, can handle dicts stored in a dict (but
not nested more than that), and can distinguish between requirements
and optional features for data that has been processed at different
points in time.
"""

_NONCHEATING_OPTIONS = {"options": {
    "startingPlayer": 0,
    "deckPlays": False,
    "emptyClues": False,
    "oneExtraCard": False,
    "oneLessCard": False,
    "allOrNothing": False,
    "detrimentalCharacters": False,
}}

def _equality_function(x, y): 
    return x == y


# This should be refactored to allow for arbitrarily nested dicts (ew!)
# eventually. Requiring that Restriction.necessary and .optional only
# contain values that are of type Restriction or non-dict types like
# bool, int, string, maybe list? In other words, we can deal with the
# problem of nested dictionaries more cleanly by recursing through
# Restriction objects.
class Restriction:
    """Stores restrictions in two separate dictionaries to trigger
    different error handling.

    self.necessary_constraints requires data to have values for each key
    and will throw an error if self.panic is set to True, otherwise will
    return False if asked to validate.

    self.optional_constraints will return True if asked to validate so
    long as data does not contain an incorrect value for any of its
    keys. If the data does not contain that key, no error will be thrown
    and validate may still return True.
    """

    def __init__(self, necessary, optional, panic=False):
        self.necessary_constraints = necessary
        self._prune_duplicates(optional)
        self.optional_constraints = optional
        self.special_cases = {}
        self.panic = panic

    def _prune_duplicates(self, data):
        """Helper function for initialization."""
        for key in self.necessary_constraints:
            if key in data and not isinstance(key, dict):
                del data[key]

    def _evaluate(self, option, key=None):
        """Returns a function that can validate whether or not the data
        qualifies for this option of the restriction. This function
        takes two inputs of the same type.

        If no special case was previously specified, then returns a
        function that evaluates to True if and only if its two inputs
        are equal.
        """
        if option not in self.special_cases:
            return _equality_function
        if key is None:
            return self.special_cases[option]
        if key not in self.special_cases[option]:
            return _equality_function
        return self.special_cases[option][key]

    def add_special_case(self, option, func):
        """If a particular option in the restriction needs to be
        evaluated by a special function func, then this method saves
        func in class variable self.special_cases.
        """
        if isinstance(option, dict):
            if option in self.special_cases:
                self.special_cases[option] = {}
            for key in option:
                self.special_cases[option][key] = func
        else:
            self.special_cases[option] = func

    def add_less_than(self, option):
        """Common function "<" gets its own method."""
        def func(x, y): return x < y
        self.add_special_case(option, func)

    def add_greater_than(self, option):
        """Common function ">" gets its own method."""
        def func(x, y): return x > y
        self.add_special_case(option, func)

    def validate(self, data):
        """This function is the purpose of the entire class.
        
        Takes dict data as input (commonly JSONs or processed game data)
        and returns True if and only if the data satisfies all
        constraints specified in this class. If the self.panic option
        was enabled, then this will return if data is missing any
        necessary keys.

        Raises an Exception if and only if data is missing a key in
        self.necessary_constraints. This should never happen.

        Returns False if any constraint is not met.
        """
        for option in self.necessary_constraints:
            if option not in data:
                if not self.panic:
                    return False
                print(data)
                raise KeyError(f'Something has gone terribly wrong. Missing \
                    {option}.')

            element = data[option]
            if not isinstance(element, dict):
                value = self.necessary_constraints[option]
                if self._evaluate(option)(element, value):
                    # data satisfies this option, so now check next
                    continue
                return False

            options = element
            # now we iterate over the nested dictionary
            for key in self.necessary_constraints[option]:
                if key not in options:
                    if not self.panic:
                        return False
                    print(data)
                    print(options)
                    raise KeyError(f'Something has gone terribly wrong. \
                        Missing {key} in {option}.')

                value = self.necessary_constraints[option][key]
                if self._evaluate(option, key)(value, data[option][key]):
                    # data satisfies this options key, so now check next
                    continue
                return False

        # beware of errors in the following. changed the above and not
        # this yet (but it currently is not used by anything)
        for option in self.optional_constraints:
            if option not in data:
                continue
            if not isinstance(option, dict):
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


# TODO: deepcopy NONCHEATING_OPTIONS in here to clean up code
def get_standard_restrictions(num_players=None):
    """Returns a Restriction that removes different games, cheaters,
    speedrunners, and games that were ended very early.
    """
    only_good_games = {
        "options": {
            "startingPlayer": 0,
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
    if num_players:
        only_good_games["options"]["numPlayers"] = num_players
    # WARNING: I'm not sure where numTurns vs turn_count is used, so
    # this may not be compatible over different formats. In that case,
    # such checks might need to be moved to optional if data processing
    # may change the name of this key.

    standard = Restriction(only_good_games, {"cheated": False})
    standard.add_greater_than("numTurns")

    return standard

NONCHEATING_RESTRICTION = Restriction(_NONCHEATING_OPTIONS, {"cheated": False})
STANDARD_GAME_RESTRICTION = get_standard_restrictions()
MAX_SCORE_ONLY = Restriction({"score": 25}, {})
MAX_SCORE30_ONLY = Restriction({"score": 30}, {})
STANDARD_2P = get_standard_restrictions(2)
