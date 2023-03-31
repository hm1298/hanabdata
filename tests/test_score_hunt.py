"""Tests score hunt. Checks which implementation is faster."""

from hanabdata.score_hunt import analyze_2P_score_hunt, analyze_2P_score_hunt2, analyze_2P_score_hunt3

def test_2P_score_hunt(benchmark):
    """Tests the main function."""
    benchmark(analyze_2P_score_hunt, 'haltmark')

def test_2P_score_hunt2(benchmark):
    """Tests the replacement function."""
    benchmark(analyze_2P_score_hunt2, 'haltmark')

def test_2P_score_hunt3(benchmark):
    """Tests the second replacement function."""
    benchmark(analyze_2P_score_hunt3, 'haltmark')