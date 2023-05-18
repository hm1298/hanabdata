"""Uses TrueSkill to assign ratings to users and variants."""

from math import sqrt
import trueskill
from trueskill import BETA, DRAW_PROBABILITY, MU, SIGMA, TAU

# oops, trueskill gets very mad if you try to compare different types
# of ratings. I will probably just go ahead and delete these TBD
class UserRating(trueskill.Rating):
    """Rating for users."""
    def __init__(self, mu=None, sigma=None, name=None):
        self.name = name
        super().__init__(mu, sigma)
    def update(self, rating):
        """Updates rating."""
        self.mu = rating.mu
        self.sigma = rating.sigma

class VariantRating(trueskill.Rating):
    """Rating for variants."""
    def __init__(self, mu=None, sigma=None, name=None):
        self.name = name
        super().__init__(mu, sigma)
    def update(self, rating):
        """Updates rating."""
        self.mu = rating.mu
        self.sigma = rating.sigma

class NamedRating(trueskill.Rating):
    """Rating for users."""
    def __init__(self, mu=None, sigma=None, name=None):
        self.name = name
        super().__init__(mu, sigma)
    def update(self, rating):
        """Updates rating."""
        self.mu = rating.mu
        self.sigma = rating.sigma

class Leaderboard(trueskill.TrueSkill):
    """Environment for storing our ratings."""
    def __init__(self, mu=MU, sigma=SIGMA, beta=BETA, tau=TAU, draw_probability=DRAW_PROBABILITY, backend=None):
        self.variants = {}
        self.users = {}
        self.variant_mu = mu
        self.variant_sigma = sigma
        super().__init__(mu, sigma, beta, tau, draw_probability, backend)

    def set_variant_rating(self, mu, sigma=None, modify_beta=False):
        """Sets variant rating"""
        self.variant_mu = mu
        if sigma is None:
            sigma = mu / 3
        self.variant_sigma = sigma

        if modify_beta:
            self.beta = self.variant_sigma / 2

    def get_variants(self):
        """Returns variants in CSV format, sorted by exposure."""
        header = ["Game Type", "Variant Name", "Num Players", "Average", "Variance", "Exposure"]
        table = []
        for name, rating in self.variants.items():
            table.append([
                f"{name[0]} {name[1]}p",
                name[0],
                name[1],
                rating.mu,
                rating.sigma,
                self.expose(rating)
            ])
        return [header] + sorted(table, key=lambda x: -x[5])

    def get_users(self):
        """Returns users in CSV format, sorted by exposure."""
        header = ["User", "Average", "Variance", "Exposure"]
        table = []
        for name, rating in self.users.items():
            table.append([
                name,
                rating.mu,
                rating.sigma,
                self.expose(rating)
            ])
        return [header] + sorted(table, key=lambda x: -x[3])

    def create_rating(self, mu=None, sigma=None, is_variant=False):
        """Specify name."""
        if mu is None:
            mu = self.variant_mu if is_variant else self.mu
        if sigma is None:
            sigma = self.variant_sigma if is_variant else self.sigma
        return trueskill.Rating(mu, sigma)

    def update_and_rate(self, variant, player_list, won, update_var=True):
        """Updates and rates based on variant and player names."""
        rating_groups = [
            (self.variants.setdefault(variant, self.create_rating(is_variant=True)),),
            tuple(self.users.setdefault(player, self.create_rating()) for player in player_list)
        ]

        # print("before:", rating_groups)

        if won:
            rated_rating_groups = self.rate(rating_groups, ranks=[1, 0])
        else:
            rated_rating_groups = self.rate(rating_groups, ranks=[0, 1])

        # print("after:", rated_rating_groups)

        if update_var:
            self.variants[variant] = rated_rating_groups[0][0]
        for index, player in enumerate(player_list):
            self.users[player] = rated_rating_groups[1][index]

        return rated_rating_groups

def get_average_of_column(table, index):
    """Returns the average of column index in a CSV table."""
    assert len(table) > 1
    total = 0.0
    for i, line in enumerate(table):
        if i == 0:
            continue
        total += line[index]
    return total / (len(table) - 1)
