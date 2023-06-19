"""Tests fetch."""

from hanabdata.tools.io import fetch

HALTMARK = "https://hanab.live/api/v1/history-full/haltmark"
LANVIN = "https://hanab.live/api/v1/history-full/Lanvin"
SODIUMDEBT = "https://hanab.live/api/v1/history-full/sodiumdebt"

def test_fetch_url1():
    """Checks fetch URL for a small user."""
    data, errored = fetch.fetch_url(HALTMARK)
    assert not errored and len(data) == 1

def test_fetch_url2():
    """Checks fetch URL for a medium user."""
    data, errored = fetch.fetch_url(SODIUMDEBT)
    assert not errored and len(data) > 1700 and len(data) < 3000

def test_fetch_url3():
    """Checks fetch URL for a large user."""
    data, errored = fetch.fetch_url(LANVIN)
    assert errored is not None and data == []

def test_fetch_user0():
    """Checks fetch user for a nil user."""
    assert fetch.fetch_user("ballpark") == []

def test_fetch_user1():
    """Checks fetch user for a small user."""
    assert len(fetch.fetch_user("haltmark")) == 1

def test_fetch_user2():
    """Checks fetch user for a medium user."""
    num_games = len(fetch.fetch_user("sodiumdebt"))
    assert 1700 < num_games < 3000

def test_fetch_user3():
    """Checks fetch user for a large user."""
    num_games = len(fetch.fetch_user("Lanvin"))
    assert 21000 < num_games < 23000

def test_fetch_game():
    """Checks fetch game returns a nonempty dict."""
    data = fetch.fetch_game("874778")
    assert data and isinstance(data, dict)

def test_fetch_seed():
    """Checks fetch seed returns a nonempty list containing dicts."""
    data = fetch.fetch_seed("p2v0s0")
    assert data and isinstance(data, list) and isinstance(data[0], dict)
