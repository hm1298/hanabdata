"""This class runs an analysis on a defined set of games."""

import itertools
from hanabdata.tools.io import read

class Analysis:
    """Analysis permits data analysis on downloaded games."""
    def __init__(self, func, write_to_file=""):
        self.data = iter([])
        self.interpret = func
        self.filter = None
        self.goal = None
        if write_to_file:
            self.write = True
            self.file = write_to_file  # make smarter?
        else:
            self.write = False

    def add_data(self, new_data):
        """Adds iterable input to self.data."""
        self.data = itertools.chain(self.data, new_data)

    def get_next_element(self):
        """Returns next element of self.data."""
        return next(self.data, None)

    def set_filter(self, restriction):
        """Setter method for self.filter."""
        self.filter = restriction

    def set_goal(self, restriction):
        """Setter method for self.goal."""
        self.goal = restriction

    def set_interpret(self, func):
        """Setter method for self.interpret."""
        self.interpret = func

    def update_file(self, data):
        """Updates file if needed."""
        if self.write:
            read.write_csv(self.file, data)

    # these next two methods are rough and probably should be removed
    # until needed. not sure what all this class should do yet
    def make_interpret_use_restrictions(self):
        """Modifies self.interpret to use restrictions.

        Note this can apply only if self.interpret does not already
        iterate. Therefore, it calls self.make_interpret_iterate()
        after adding the restriction. Do not call this method if
        self.interpret already uses restrictions or iterates.
        """
        def func(x, y, z):
            if y.validate(x):
                temp = self.interpret(x)
                if z.validate(x):
                    return temp, True
                return temp, False
            return None, False
        self.interpret = func

        def average_ints(x):
            swapped = [[] * len(x[0])]
            result = []
            for k in x:
                for i in k:
                    swapped.append(i)
            for c in swapped:
                if isinstance(c[0], (int, float)):
                    result.append(sum(c) / len(c))
            return result

        self.make_interpret_iterate(average_ints)

    def make_interpret_iterate(self, combine):
        """Modifies self.interpret to iterate over many games.

        If self.interpret only interprets a single game, this easily
        generalizes that. Do not call this method if self.interpret
        already iterates.
        """
        def func(x, y, z):
            result = []
            for i in x:
                output, status = self.interpret(i, y, z)
                if output is None:
                    continue
                # not quite sure what to do here
                if status:
                    result.append(output)
            return combine(result)
        self.interpret = func

    def analyze(self):
        """Runs the analysis. Depletes self.data."""
        result = self.interpret(self.data, self.filter, self.goal)
        self.update_file(result)
        assert next(self.data, None) is None
        return result

# def score_hunt_analysis():
#     """Model function."""
#     get_data()  # should data instead be passed into function? maybe yes

#     initialize_table()  # column headers, maybe call label_columns()?
#     while True:  # iterate through data
#         filter_out_bad_entries()  # will be done with restriction
#         info = get_info_from_entry()

#         success = goal_condition()
#         if check_row(info):
#             initialize_row()
#         update_table(info, success)
