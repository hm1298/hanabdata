"""
This contains the basic logic for dealing with variants.
"""
# pylint: disable=invalid-name

import json
import random
import requests
from tools.fetch import MAX_TIME


# pylint: disable-next=line-too-long
VARIANT_URL = "https://raw.githubusercontent.com/Hanabi-Live/hanabi-live/main/packages/data/src/json/variants.json"
VARIANT_PATH = './tools/variants.json'


class VariantJSON(json.JSONEncoder):
    """Encodes JSON into a temporary object."""
    def default(self, o):
        return o.__dict__


class Variant(object):
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

if random.random() > 0.98:
    update_variants()

def get_variant_list():
    """Returns Variant list as saved in file."""
    with open(VARIANT_PATH, encoding="utf8") as json_file:
        variant_list = json.load(json_file)
    return variant_list

def find_variant(variant_id):
    """Returns Variant object with given variant_id."""

    correct_variant_data = None
    for variant in VARIANT_LIST:
        if variant["id"] == variant_id:
            correct_variant_data = variant

    found_variant = Variant(**correct_variant_data)
    return found_variant

VARIANT_LIST = get_variant_list()
