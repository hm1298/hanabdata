"""Determines number of attempts and total duration of play time
leading up to a player's first win in each variant. Prints to a CSV in
data/processed/score_hunts.
"""

import datetime
from hanabdata.tools.analysis import Analysis
from hanabdata.tools.restriction import STANDARD_2P, has_winning_score 
from hanabdata.tools.structures import User, ScoreHuntData
def analyze_2P_score_hunt(username: str, restriction=STANDARD_2P):
    """A function that creates the CSV in the original for loop."""

    data = User.load(username).data

    # table stores the information for the CSV writer, and score_hunt
    # stores the table indices for each variant
    table = [['variant', 'max score', 'won', 'duration', 'attempts']]
    score_hunt = {}
    # we cycle through in forwards chronological order
    for game in reversed(data):
        if not restriction.validate(game):
            # note: the standard restriction throws out games with less
            # than 3 turns. this may boost some player's numbers to an
            # unfair extent, depending on scorehunting strategy
            continue
        variant = game['options']['variantName']
        variant_id = game['options']['variantID']
        start_time = datetime.datetime.fromisoformat(game['datetimeStarted'])
        end_time = datetime.datetime.fromisoformat(game['datetimeFinished'])
        score = game['score']
        duration = (end_time - start_time).total_seconds()
        win = has_winning_score(game)

        if variant_id not in score_hunt:
            score_hunt[variant_id] = len(table)
            table.append([variant, score, win, duration, 1])
        else:
            line = table[score_hunt[variant_id]]
            if line[2]:
                continue
            # updates max score
            line[1] = max(line[1], score)
            # updates win status to True if necessary
            line[2] = win
            # adds to duration & attempts
            line[3] += duration
            line[4] += 1

    ScoreHuntData(table, username).save()


class ScoreHunt(Analysis):
    """A score hunt class."""
    def analyze(self):
        """Analyzes."""
        self.refresh()
        for game in self.data:
            self.parse(game)
        self.cleanup()
        self.update_file(self.table)
        assert next(self.data, None) is None
        return self.table

    def cleanup(self):
        """Changes "won" column in table to True or False values."""
        lines = iter(self.table)
        next(lines)
        for line in lines:
            if line[2]:
                line[2] = True

    def refresh(self):
        """Clears instance variables if already used."""
        self.table = [['variant', 'max score', 'won', 'duration', 'attempts']]
        self.score_hunt = {}
        self.processed = {}
        self.ooo = False
        self.current = None

    def parse(self, game):
        """Parses."""
        game_id = game['id']
        if not self.filter.validate(game) and game_id not in self.processed:
                return
        if self.current and game_id < self.current:
            self.ooo = True

        variant = game['options']['variantName']
        variant_id = game['options']['variantID']
        score = game['score']
        duration = self._helper_for_time(game)
        won = has_winning_score(game)

        if variant_id not in self.score_hunt:
            self.score_hunt[variant_id] = len(self.table)
            self.table.append([variant, 0, False, 0, 0])

        line = self.table[self.score_hunt[variant_id]]
        if line[2]:
            if game_id >= line[2]:
                return
        # updates max score
        line[1] = max(line[1], score)
        # updates win status to True if necessary
        if won:
            line[2] = game_id
            if self.ooo:
                line[3], line[4] = self._helper_ooo_games(game_id, variant_id)
        # adds to duration & attempts
        line[3] += duration
        line[4] += 1

        self.processed[game_id] = (duration, variant_id)
        self.current = game_id


    def _helper_for_time(self, game):
        """Returns duration of a game."""
        start_time = datetime.datetime.fromisoformat(game['datetimeStarted'])
        end_time = datetime.datetime.fromisoformat(game['datetimeFinished'])
        return (end_time - start_time).total_seconds()

    def _helper_ooo_games(self, game_id, variant_id):
        """Returns the correct duration and number of attempts.

        Only called when self.data has a chronologically earlier
        winning game after a chronologically later winning game.
        """
        duration, attempts = 0, 0
        for temp_id, info in self.processed.items():
            temp_dur, temp_var = info
            if temp_id < game_id and temp_var == variant_id:
                duration += temp_dur
                attempts += 1
        return duration, attempts


def scorehunt_with_class(username: str, restriction=STANDARD_2P):
    """Hi."""
    def dummy_func(x, y, z): return x + y + z
    file_path = f'./data/processed/score_hunts/{username}.csv'
    sh = ScoreHunt(dummy_func, write_to_file=file_path)
    sh.set_filter(restriction)
    sh.add_data(reversed(User.load(username).data))
    sh.analyze()

if __name__ == '__main__':
    # file_path1 = './data/processed/score_hunts/hallmark (temp).csv'
    # file_path2 = './data/processed/score_hunts/hallmark.csv'
    # data1 = [tuple(i) for i in _read_csv(file_path1)]
    # data2 = [tuple(i) for i in _read_csv(file_path2)]
    # difference = set(data1).symmetric_difference(set(data2))
    # dct = {}
    # for line in list(difference):
    #     d, a = float(line[3]), int(line[4])
    #     if line[0] not in dct:
    #         dct[line[0]] = (d, a)
    #     else:
    #         d2, a2 = dct[line[0]]
    #         print(d - d2, a - a2)

    username = input('username: ')
    # analyze_2P_score_hunt(username)
    scorehunt_with_class(username)
