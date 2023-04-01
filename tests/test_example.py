"""Displays how we can use pytest going forward."""

from hanabdata.tools.io.update import update_user

def test_always_passes():
    """Always passes."""
    assert True

def test_always_fails():
    """Always fails."""
    assert False

def test_update_user_does_not_error():
    """Always true. Any errors?"""
    update_user("hallmark")
    assert True
