"""The journal-club guide's numbers, the contribution verdicts, and the slide budget.

Run:
  python3 scripts/rules.py numbers                    the counts and verdicts, as JSON
  python3 scripts/rules.py slides 20                  slides per part for a 20-minute slot
  python3 scripts/rules.py slides 30 --papers 2       ... for two papers

Sources: [S1] is the instructor's guide, [S2] is this skill's own additions (see SKILL.md).
"""
from __future__ import annotations

import argparse
import json
import sys

STRENGTHS = (2, 3)       # [S1] "2-3 strengths"
LIMITATIONS = (2, 3)     # [S1] "2-3 limitations or concerns"
VERDICTS = ("supported", "partly supported", "not shown")   # [S2] contribution table

MINUTES_PER_SLIDE = 2    # [S2] a rough pace for a journal-club talk
MIN_SLIDES = 5           # [S2] title, problem, contributions, methods, results

# [S2] Slide order in the talk. Parts with 0 slides are folded into a neighbor
# (gap_scope into problem) or left out.
ORDER = ("title", "problem", "gap_scope", "contributions", "methods", "results",
         "comparison", "language", "strengths_limitations", "takeaways", "discussion")
BASE = {"title": 1, "problem": 1, "contributions": 1, "methods": 1, "results": 1}
# [S2] Which part gets the next slide as the slot grows. Most of the extra time goes to
# parts 2-4 (contributions, methods, results), as the guide's emphasis suggests.
EXTRA_ONE_PAPER = ("strengths_limitations", "takeaways", "results", "language", "gap_scope",
                   "methods", "discussion", "results", "methods")
EXTRA_MORE_PAPERS = ("strengths_limitations", "takeaways", "comparison", "results", "language",
                     "gap_scope", "methods", "discussion", "comparison", "results", "methods")


def slide_budget(minutes: float, papers: int = 1) -> dict:
    """Slides per part for a slot of `minutes` presenting `papers` papers."""
    if minutes < MIN_SLIDES * MINUTES_PER_SLIDE / 2:
        return {"error": f"a {minutes}-minute slot is too short for a review; "
                         f"ask the presenter for the real slot length"}
    if papers < 1:
        return {"error": "papers must be 1 or more"}
    total = max(MIN_SLIDES, round(minutes / MINUTES_PER_SLIDE))
    counts = dict(BASE)
    extras = EXTRA_ONE_PAPER if papers == 1 else EXTRA_MORE_PAPERS
    i = 0
    while sum(counts.values()) < total:
        part = extras[i] if i < len(extras) else ("results", "methods")[(i - len(extras)) % 2]
        counts[part] = counts.get(part, 0) + 1
        i += 1
    slides = [{"part": p, "count": counts[p]} for p in ORDER if counts.get(p)]
    note = []
    if not counts.get("gap_scope"):
        note.append("gap and scope go on the problem slide")
    if papers > 1 and not counts.get("comparison"):
        note.append("no room for a comparison slide: put the comparison in the results slides")
    return {"minutes": minutes, "papers": papers, "total": sum(counts.values()),
            "slides": slides, "note": "; ".join(note)}


def numbers() -> dict:
    return {"strengths": list(STRENGTHS), "limitations": list(LIMITATIONS),
            "verdicts": list(VERDICTS), "minutes_per_slide": MINUTES_PER_SLIDE}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("numbers")
    s = sub.add_parser("slides")
    s.add_argument("minutes", type=float)
    s.add_argument("--papers", type=int, default=1)
    args = ap.parse_args(argv)
    out = numbers() if args.cmd == "numbers" else slide_budget(args.minutes, args.papers)
    print(json.dumps(out, indent=2))
    return 1 if "error" in out else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
