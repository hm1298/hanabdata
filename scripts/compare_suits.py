"""Compares some basic suits."""

from hanabdata.game.variants import find_variant_from_name
from hanabdata.tools.io.read import _read_csv

SUITS_DARKIFIED = {"Red": "Black", "Prism": "Dark Prism", "Rainbow": "Dark Rainbow", "Pink": "Dark Pink", "Muddy Rainbow": "Cocoa Rainbow", "White": "Gray", "Brown": "Dark Brown", "Omni": "Dark Omni", "Light Pink": "Gray Pink", "Null": "Dark Null"}

def average_ratings(lookup_table, suit_name):
    """Compares"""
    rating_sum, total = 0.0, 0
    for line in lookup_table:
        variant_name = line[1]
        if check_suit_in_variant(suit_name, variant_name):
            rating_sum += float(line[3])
            total += 1
    return rating_sum / total

def check_suit_in_variant(suit_name, variant_name):
    """Returns true if suit_name is in Variant with variant_name."""
    return suit_name in find_variant_from_name(variant_name).suits

if __name__ == "__main__":
    for i in range(2, 7):
        if i > 2:
            break
        table = _read_csv(f"./data/processed/ratings/variants_iter1.csv")
        table.pop(0)
        simple_suits, dark_suits = {}, {}
        for simple, dark in SUITS_DARKIFIED.items():
            simple_suits[simple] = average_ratings(table, simple)
            dark_suits[dark] = average_ratings(table, dark)
        lb_simple = sorted(simple_suits.items(), key=lambda x: -x[1])
        lb_dark = sorted(dark_suits.items(), key=lambda x: -x[1])
        print(f"For teams with any number of players, variants with the given simple suit have average rating:")
        for j, rating_pair in enumerate(lb_simple):
            if len(rating_pair[0]) > 7:
                print(f"{j + 1}\t{rating_pair[0]}\t{rating_pair[1]:.4f}")
            else:
                print(f"{j + 1}\t{rating_pair[0]}\t\t{rating_pair[1]:.4f}")
        print(f"For teams with any number of players, variants with the given dark suit have average rating:")
        for j, rating_pair in enumerate(lb_dark):
            if len(rating_pair[0]) > 7:
                print(f"{j + 1}\t{rating_pair[0]}\t{rating_pair[1]:.4f}")
            else:
                print(f"{j + 1}\t{rating_pair[0]}\t\t{rating_pair[1]:.4f}")