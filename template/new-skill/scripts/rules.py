"""The source's rules as code: numbers, times and thresholds the agent must never guess.

Each function returns its answer AND the piece id it comes from, so the answer can cite it.
Keep one function per rule, and write the source's exact words in its docstring.

Run (from the skill folder):
  python3 scripts/rules.py example 12.5
"""
from __future__ import annotations

import argparse
import json


def example_rule(value: float) -> dict:
    """TODO: replace with one rule from your source.

    Source: TODO piece id, page — "the source's exact words".
    """
    raise NotImplementedError("TODO: write this rule from your source, then test it")


def main() -> None:
    ap = argparse.ArgumentParser(description="The source's rules as code.")
    sub = ap.add_subparsers(dest="rule", required=True)
    ex = sub.add_parser("example", help="TODO: what the rule answers")
    ex.add_argument("value", type=float)
    a = ap.parse_args()
    if a.rule == "example":
        print(json.dumps(example_rule(a.value), indent=1))


if __name__ == "__main__":
    main()
