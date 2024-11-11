"""A collection of simple questions to ask my game database."""

from collections import Counter
from tqdm import tqdm
from hanabdata.tools.restriction import Restriction, get_standard_restrictions
from hanabdata.tools.structures import GamesIterator

def popular_variants(restriction=None, date=None):
    """Finds number of games played in each variant satisfying restriction that have occurred since date.

    date: string satisfying format "2024-01-01T00:00:00Z"
    """
    if restriction is None:
        # Currently, these are my default restrictions. Can change
        restriction = get_standard_restrictions()
        del restriction.necessary_constraints["numTurns"]

    restriction.add_greater_than("datetimeStarted")
    if date is None:
        date = "2000-01-01T00:00:00Z"
    restriction.necessary_constraints["datetimeStarted"] = date

    variant_to_count = Counter()
    for game in tqdm(GamesIterator(), total=1200000):
        if not restriction.validate(game):
            continue
        variant_to_count[game["options"]["variantName"]] += 1

    results = [(count, variant_name) for variant_name, count in variant_to_count.items()]
    results.sort(reverse=True)

    print(results[:10])

    return results

if __name__ == "__main__":
    ans = popular_variants(date="2023-12-11T00:00:00Z")
    ans2 = popular_variants(restriction=Restriction({}, {}), date="2023-12-11T00:00:00Z")
    print("With standard options enabled, the most popular variants since the day of the last variant release are:")
    print("".ljust(4, ' '), "Variant Name".ljust(30, ' '), "Games")
    for i, row in enumerate(ans[:20]):
        print(str(i + 1).ljust(4, ' '), row[1].ljust(30, ' '), row[0])

    print("\nWith any options enabled, the most popular variants since the day of the last variant release are:")
    print("".ljust(4, ' '), "Variant Name".ljust(30, ' '), "Games")
    for i, row in enumerate(ans2[:20]):
        print(str(i + 1).ljust(4, ' '), row[1].ljust(30, ' '), row[0])
