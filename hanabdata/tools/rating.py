"""Uses TrueSkill to assign ratings to users and variants."""

import math
import trueskill
from trueskill import BETA, DRAW_PROBABILITY, MU, SIGMA, TAU


class Leaderboard():
    """Manages multiple Trueskill environments."""
    def __init__(self, team_sizes: list, variant_mu=MU):
        self.envs = {}
        for num_players in team_sizes:
            self.envs[num_players] = trueskill.TrueSkill(beta=math.sqrt(3/num_players)*BETA, draw_probability=0.0)
            self.curr_env = self.envs[num_players]

        self.variant_mu = variant_mu

        self.users = {}
        self.variants = {}

    def update(self, variant, player_list, won, update_var=True):
        """Controls most stuff."""
        env = self.envs[variant[1]]
        variant_rating = self.variants.setdefault(variant, env.create_rating(mu=self.variant_mu, sigma=math.sqrt(3/variant[1])*self.variant_mu/3))
        rating_groups = [
            tuple(variant_rating for i in range(variant[1])),
            tuple(self.users.setdefault(player, env.create_rating()) for player in player_list)
        ]

        if won:
            rated_rating_groups = env.rate(rating_groups, ranks=[1, 0])
        else:
            rated_rating_groups = env.rate(rating_groups, ranks=[0, 1])

        if update_var:
            self.variants[variant] = rated_rating_groups[0][0]
        for index, player in enumerate(player_list):
            self.users[player] = rated_rating_groups[1][index]

        return rated_rating_groups

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
                self.curr_env.expose(rating)
            ])
        return [header] + sorted(table, key=lambda x: -x[5])

    def set_variants(self, table):
        """Sets variants to predetermined values.

        Takes as input a CSV format. Should be used in conjunction with
        self.update_and_rate(...)'s paramater update_var set to False.
        """
        csv_iter = iter(table)
        header = next(csv_iter)
        index_mu = header.index("Average")
        index_sigma = header.index("Variance")
        for line in csv_iter:
            self.variants[(line[1], int(line[2]))] = self.curr_env.create_rating(mu=float(line[index_mu]), sigma=float(line[index_sigma]))
        print("Finished setting variant ratings.")

    def get_users(self):
        """Returns users in CSV format, sorted by exposure."""
        header = ["User", "Average", "Variance", "Exposure"]
        table = []
        for name, rating in self.users.items():
            table.append([
                name,
                rating.mu,
                rating.sigma,
                self.curr_env.expose(rating)
            ])
        return [header] + sorted(table, key=lambda x: -x[3])

    def get_player_ranking(self, player_name):
        """Returns player ranking among all players in self.users."""
        if player_name not in self.users:
            return None
        player_rating = self.curr_env.expose(self.users[player_name])
        player_ranking = 1
        for _, rating in self.users.items():
            user_rating = self.curr_env.expose(rating)
            if player_rating < user_rating:
                player_ranking += 1
        return player_ranking


class LBEnvironment(trueskill.TrueSkill):
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

    def set_variants(self, table):
        """Sets variants to predetermined values.

        Takes as input a CSV format. Should be used in conjunction with
        self.update_and_rate(...)'s paramater update_var set to False.
        """
        csv_iter = iter(table)
        header = next(csv_iter)
        index_mu = header.index("Average")
        # index_sigma = header.index("Variance")
        for line in csv_iter:
            line_mu = float(line[index_mu])
            self.variants[(line[1], int(line[2]))] = self.create_rating(mu=line_mu, sigma=line_mu/3, is_variant=True)
        print("Finished setting variant ratings.")

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
        variant_rating = self.variants.setdefault(variant, self.create_rating(is_variant=True))
        rating_groups = [
            tuple(variant_rating for i in range(variant[1])),
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

    def get_player_ranking(self, player_name):
        """Returns player ranking among all players in self.users."""
        if player_name not in self.users:
            return None
        player_rating = self.expose(self.users[player_name])
        player_ranking = 1
        for _, rating in self.users.items():
            user_rating = self.expose(rating)
            if player_rating < user_rating:
                player_ranking += 1
        return player_ranking


class LBSoloEnvironment(LBEnvironment):
    """Different "game" definition."""
    def update_and_rate(self, variant, player_list, won, update_var=True):
        """Each game has update rule:
        - Variant updates rating based on team game against all players.
        - Each player updates rating based on solo game against variant.
        """
        try:
            variant_rating = self.variants[variant]
        except KeyError:
            self.variants[variant] = self.create_rating(is_variant=True)
            variant_rating = self.variants[variant]
        player_ratings = [
            self.users.setdefault(
                player,
                self.create_rating()
            ) for player in player_list
        ]

        if won:
            ranks=[1, 0]
        else:
            ranks = [0, 1]

        for index, player in enumerate(player_list):
            rating_groups = [
                (variant_rating,),
                (player_ratings[index],)
            ]
            rated_rating_groups = self.rate(rating_groups, ranks=ranks)

            self.users[player] = rated_rating_groups[1][0]

        if update_var:
            rating_groups = [
                (variant_rating for _ in player_ratings),
                tuple(player_ratings)
            ]
            self.variants[variant] = rated_rating_groups[0][0]

        return rated_rating_groups  # not super useful atm

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


class MatchPointLB(LBEnvironment):
    """Leaderboard for users only; no variant ratings tracked.

    Make sure to initialize with large draw_probability. See method
    MatchPointLB.update_and_rate() for more info.
    """
    seeds = {}

    def update_and_rate(self, game, won):
        """Updates user ratings according to the following rule.

        The team of N players have current ratings. They play a N:...:N
        free-for-all against all previous players of the seed, using old
        ratings. A perfect score ensures a first place finish, and a less
        than perfect score ensures a last place finish. Two teams that
        both receive a perfect score or both do not receive a perfect
        score are said to have tied.

        Old player ratings are saved before update from playing the seed.
        """
        player_list = game["playerNames"]
        player_ratings = tuple(
            self.users.setdefault(
                player,
                self.create_rating()
            ) for player in player_list
        )

        rank_value = 0 if won else 1
        ranks, rating_groups = [rank_value], [player_ratings]

        for match in self.seeds.setdefault(game["seed"], []):
            ranks.append(match[0])
            rating_groups.append(match[1])
        self.seeds[game["seed"]].append((rank_value, player_ratings))
        if len(rating_groups) == 1:
            return

        new_ratings = self.rate(rating_groups, ranks=ranks)[0]
        for i, player in enumerate(player_list):
            self.users[player] = new_ratings[i]


def get_average_of_column(table, index):
    """Returns the average of column index in a CSV table."""
    assert len(table) > 1
    total = 0.0
    for i, line in enumerate(table):
        if i == 0:
            continue
        total += line[index]
    return total / (len(table) - 1)
