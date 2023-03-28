"""
This contains the basic logic for dealing with suits.
"""

import json
import requests
from tools.fetch import MAX_TIME


SUIT_URL = "https://raw.githubusercontent.com/Hanabi-Live/hanabi-live/main/packages/data/src/json/suits.json"
SUIT_PATH = './tools/suits.json'


class SuitJSON(json.JSONEncoder):
    """Encodes JSON into a temporary object."""
    def default(self, o):
        return o.__dict__


class Suit(object):
    """Defines a class for variants."""
    # pylint: disable-next=redefined-builtin
    def __init__(self, name, id, abbreviation):
        self.name = name
        self.id = id
        self.abbreviation = abbreviation


def get_suit_list():
    """Returns suit list as saved in file."""
    with open(SUIT_PATH, encoding="utf8") as json_file:
        suit_list = json.load(json_file)
    return suit_list

def update_suits():
    """Pulls from github."""
    response = requests.get(SUIT_URL, timeout=MAX_TIME).json()
    with open(SUIT_PATH, 'w', encoding="utf8") as json_file:
        json.dump(response, json_file)
    print("Updated suits.")

def find_suit(suit_id):
    """Returns Suit object with given suit_id."""

    correct_suit_data = None
    for suit in SUIT_LIST:
        if suit["id"] == suit_id:
            correct_suit_data = suit

    found_suit = Suit(**correct_suit_data)

SUIT_LIST = get_suit_list()