"""Uses TrueSkill to assign ratings to users and variants."""

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
        super().__init__(mu, sigma, beta, tau, draw_probability, backend)

    def get_variants(self):
        """Simple getter function."""
        return sorted(self.variants.items(), key=lambda x: self.expose(x[1]), reverse=True)

    def get_users(self):
        """Simple getter function."""
        return sorted(self.users.items(), key=lambda x: self.expose(x[1]), reverse=True)

    def create_rating(self, mu=None, sigma=None, name="test", is_variant=False):
        """Specify name."""
        if mu is None:
            mu = self.mu
        if sigma is None:
            sigma = self.sigma
        if is_variant:
            new_var = trueskill.Rating(mu, sigma)
            self.variants[name] = new_var
            return new_var
        new_user = trueskill.Rating(mu, sigma)
        self.users[name] = new_user
        return new_user

    def update_and_rate(self, variant, player_list, won):
        """Updates and rates based on variant and player names."""
        rating_groups = [
            (self.variants.setdefault(variant, self.create_rating(name=variant, is_variant=True)),),
            tuple(self.users.setdefault(player, self.create_rating(name=player)) for player in player_list)
        ]

        if won:
            rated_rating_groups = self.rate(rating_groups, ranks=[1, 0])
        else:
            rated_rating_groups = self.rate(rating_groups, ranks=[0, 1])

        self.variants[variant] = rated_rating_groups[0][0]
        for index, player in enumerate(player_list):
            self.users[player] = rated_rating_groups[1][index]

        return rated_rating_groups

env = Leaderboard(draw_probability=0.0)
