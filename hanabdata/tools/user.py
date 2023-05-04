"""This class helps with user data analysis."""

from hanabdata.tools.io.read import read_user, user_data_exists, get_score_hunt, write_user
from hanabdata.tools.io.fetch import fetch_user
from hanabdata.tools.io.update import update_user
from hanabdata.score_hunt import analyze_2P_score_hunt
from hanabdata.tools.restriction import get_standard_restrictions

class User:
    """User stores info from the site on a player.

    Controls whether or not data gets written to file, and only loads
    into memory when first accessed.
    """
    def __init__(self, name, update=False):
        self.name = name
        self.update = update
        self.data = None
        self.mode = None

    def get_data(self):
        """Retrieves data from file.

        If no such file, pulls from site.
        """
        if self.data is None:
            if self.update:
                update_user(self.name)

            if user_data_exists(self.name):
                data = read_user(self.name)
            else:
                data = fetch_user(self.name)
            self.data = data

        return self.data

    def set_data(self, data):
        """Sets self.data.

        Updates to file if self.update is True.
        """
        self.data = data

        if self.update:
            write_user(self.name, self.data)

    def get_score_hunt(self):
        """Retrieves score hunt from file.

        If no such file, generates score hunt report.
        """
        data = get_score_hunt(self.name)
        if data is None:
            # currently, score hunt always writes to file
            self._apply_func_to_data(analyze_2P_score_hunt)
            return get_score_hunt(self.name)
        return data

    def get_analysis(self, func):
        """Runs an analysis function on self.data.

        Returns the result. Writes to file if self.update is True.
        """
        result = self._apply_func_to_data(func)

        if self.update:
            # TODO: write to a default location, perhaps user file in
            # data/processed/users?
            pass

        return result

    def score_hunt_with_partner(self, user2):
        """Score hunt for partnerships."""
        restriction = get_standard_restrictions(2)
        restriction.add_filter("players", user2.name)
        restriction.add_contains(user2.name)
        analyze_2P_score_hunt(self.name, restriction)

    def _apply_func_to_data(self, func):
        """Applies a function to self.data."""
        return func(self.data)
