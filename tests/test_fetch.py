"""Tests fetch."""

import hanabdata.tools.io.fetch as fetch

HALTMARK = "https://hanab.live/api/v1/history-full/haltmark"
LANVIN = "https://hanab.live/api/v1/history-full/Lanvin"
SODIUMDEBT = "https://hanab.live/api/v1/history-full/sodiumdebt"

def test_fetch_url1():
    """Checks fetch URL for a small user."""
    num_games = len(fetch.fetch_url(HALTMARK))
    assert(num_games == 1)

def test_fetch_url2():
    """Checks fetch URL for a medium user."""
    num_games = len(fetch.fetch_url(SODIUMDEBT))
    assert(num_games > 1400 and num_games < 1700)

def test_fetch_url3():
    """Checks fetch URL for a large user."""
    assert(not fetch.fetch_url(LANVIN))

def test_fetch_user1():
    """Checks fetch user for a small user."""
    assert(len(fetch.fetch_user("haltmark")) == 1)

def test_fetch_user2():
    """Checks fetch user for a medium user."""
    num_games = len(fetch.fetch_user("sodiumdebt"))
    assert(num_games > 1400 and num_games < 1700)

def test_fetch_user3():
    """Checks fetch user for a large user."""
    num_games = len(fetch.fetch_user("Lanvin"))
    assert(num_games > 21000 and num_games < 23000)
