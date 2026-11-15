"""Tests for the skill's scripts.

Every expected value comes from the source or from a calculation you checked by hand,
never from a model's answer. Say where it came from in a comment.

Run (from the repository root):  python -m pytest -q skills/<your-skill-name>/evals
"""
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / "scripts"))

import rules  # noqa: E402


def test_example_rule():
    # TODO: a case where you know the right answer, and where you checked it
    # (for example: "Table 6B-3, p. 612: 45 mph, 12 ft lane -> 540 ft").
    result = rules.example_rule(12.5)
    assert result["answer"] == "TODO"


def test_example_rule_edge_case():
    # TODO: the boundary: exactly at the threshold, just below, just above.
    pass
