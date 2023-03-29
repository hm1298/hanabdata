"""Displays how we can use pytest going forward."""

from hanabdata.score_hunt import analyze_2P_score_hunt

def test_always_passes():
    """Always passes."""
    assert True

def test_always_fails():
    """Always fails."""
    assert False

# does not currently work! I haven't untangled why python works but not
# pytest quite yet. likely need to change imports within subpackages
def test_score_hunt_does_not_error():
    """Always true. Any errors?"""
    analyze_2P_score_hunt("hallmark")
    assert True