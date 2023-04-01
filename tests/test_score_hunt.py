"""Tests score hunt. Checks which implementation is faster."""

from hanabdata.score_hunt import analyze_2P_score_hunt

def test_2P_score_hunt(benchmark):
    """Tests the main function."""
    benchmark(analyze_2P_score_hunt, 'hallmark')
