"""
This contains the basic logic for dealing with variants.
"""
# pylint: disable=invalid-name

import json
import requests
from hanabdata.tools.io.fetch import MAX_TIME


VARIANT_URL = "https://raw.githubusercontent.com/Hanabi-Live/hanabi-live/main/packages/data/src/json/variants.json"
VARIANT_PATH = './data/assets/variants.json'


class VariantJSON(json.JSONEncoder):
    """Encodes JSON into a temporary object."""
    def default(self, o):
        return o.__dict__


class Variant:
    """Defines a class for variants."""
    # pylint: disable-next=redefined-builtin
    def __init__(self, id, name, suits, *args, **kwargs):
        self.id = id
        self.name = name
        self.suits = suits


def update_variants():
    """Pulls from github. To fold into io."""
    response = requests.get(VARIANT_URL, timeout=MAX_TIME).json()
    with open(VARIANT_PATH, 'w', encoding="utf8") as json_file:
        json.dump(response, json_file)
    print("Updated variants.")

def get_variant_list():
    """Returns list of Variant objects."""
    try:
        with open(VARIANT_PATH, encoding="utf8") as json_file:
            json_list = json.load(json_file)
        variant_list = []
        for variant_data in json_list:
            variant_list.append(Variant(**variant_data))
        return variant_list
    except FileNotFoundError:
        update_variants()
        return get_variant_list()

def find_variant(variant_id):
    """Returns Variant object with given variant_id."""

    correct_variant = None
    for variant in VARIANT_LIST:
        if variant.id == variant_id:
            correct_variant = variant

    if not correct_variant:
        update_variants()
        return find_variant(variant_id)

    return correct_variant

VARIANT_LIST = get_variant_list()
