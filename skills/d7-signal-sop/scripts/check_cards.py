"""Check action cards against the SOP before anyone acts on them.

What it checks, card by card:
  1. all six fields are there (Do, Who, When, SOP, Weight, Person decides);
  2. every cited clause id exists in the SOP index;
  3. every quote is the SOP's exact words (spacing and curly quotes ignored);
  4. the weight is not raised above the clause's weight ("consider" sold as "must");
  5. no card cites Appendix B or C as if it had content (both are blank);
  6. Who is not empty.

And suggestion by suggestion (experience that is NOT the SOP):
  7. all three fields are there (Suggest, From, Person decides);
  8. From cites a lesson or practice id that exists (L# in lessons.md, P# in practice.md);
  9. Person decides is "yes";
 10. a suggestion carries no SOP field or weight, so it cannot pass for the SOP.

Run (from the skill folder):
      python3 scripts/check_cards.py cards.md          (exit code 1 if any card fails)
      python3 scripts/check_cards.py cards.md --json   (machine-readable report)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # scripts/
REFS = HERE.parent / "references"
INDEX = REFS / "clauses.json"
FIELDS = ["Do", "Who", "When", "SOP", "Weight", "Person decides"]
SUGGESTION_FIELDS = ["Suggest", "From", "Person decides"]
RANK = {"consider": 0, "standard": 1, "must": 2}


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("›", ">").replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def load_index() -> dict:
    data = json.loads(INDEX.read_text())
    return {norm(c["id"]): c for c in data["clauses"]}


def experience_ids() -> set[str]:
    """L# entries in lessons.md and P# entries in practice.md."""
    ids = set()
    for name in ("lessons.md", "practice.md"):
        path = REFS / name
        if path.exists():
            ids |= set(re.findall(r"(?m)^## ([LP]\d+)\s*$", path.read_text()))
    return ids


def check_suggestion(card: dict, known: set[str]) -> list[str]:
    f, problems = card["fields"], []
    for name in SUGGESTION_FIELDS:
        if not f.get(name):
            problems.append(f"missing field: {name}")
    cited = re.findall(r"\b([LP]\d+)\b", f.get("From", ""))
    if f.get("From") and not cited:
        problems.append("From does not cite a lesson (L#) or practice entry (P#)")
    for i in cited:
        if i not in known:
            problems.append(f"{i} is not in lessons.md or practice.md")
    if f.get("Person decides") and not norm(f["Person decides"]).startswith("yes"):
        problems.append("a suggestion from experience always leaves the decision to a person")
    if "SOP" in f or "Weight" in f:
        problems.append("a suggestion is not the SOP: remove its SOP and Weight fields")
    return problems


def parse_cards(md: str) -> list[dict]:
    cards = []
    for block in re.split(r"(?m)^###\s+", md)[1:]:
        title, _, body = block.partition("\n")
        if title.strip().lower().startswith("not covered"):
            continue
        fields = {}
        for m in re.finditer(r"(?m)^[ \t]*-[ \t]*\*\*(.+?):\*\*[ \t]*(.*)$", body):
            fields[m.group(1).strip()] = m.group(2).strip()
        cards.append({"title": title.strip(), "fields": fields})
    return cards


def parse_citations(sop_field: str) -> list[tuple[str, str]]:
    """'<id> - "<quote>"; <id> - "<quote>"' -> [(id, quote), ...]"""
    out = []
    for m in re.finditer(r'([^";]+?)\s*[—–-]+\s*["“](.+?)["”](?:\s*;|\s*$)', sop_field):
        out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def check(md: str) -> list[dict]:
    index = load_index()
    known = experience_ids()
    report = []
    for card in parse_cards(md):
        if card["title"].lower().startswith("suggestion"):
            problems = check_suggestion(card, known)
            report.append({"card": card["title"], "kind": "suggestion", "ok": not problems,
                           "problems": problems, "warnings": [], "clauses": []})
            continue
        f, problems, warnings = card["fields"], [], []
        for name in FIELDS:
            if not f.get(name):
                problems.append(f"missing field: {name}")
        cites = parse_citations(f.get("SOP", ""))
        if f.get("SOP") and not cites:
            problems.append('SOP field has no "<clause id> - \\"exact words\\"" citation')
        strongest = None
        for cid, quote in cites:
            key = norm(cid)
            if "appendix b" in key or "appendix c" in key:
                problems.append(f"cites {cid}: Appendix B and C are blank in v1.5, nothing to cite")
                continue
            clause = index.get(key)
            if clause is None:
                problems.append(f"clause not in the SOP: {cid}")
                continue
            if norm(quote) not in norm(clause["text"]):
                problems.append(f"quote is not the SOP's words for {cid}: \"{quote}\"")
            if strongest is None or RANK[clause["weight"]] > RANK[strongest]:
                strongest = clause["weight"]
        w = norm(f.get("Weight", "")).split()[0] if f.get("Weight") else ""
        if strongest and w in RANK:
            if RANK[w] > RANK[strongest]:
                problems.append(f"weight raised: card says {w}, SOP says {strongest}")
            elif RANK[w] < RANK[strongest]:
                warnings.append(f"weight lowered: card says {w}, SOP says {strongest}")
        elif f.get("Weight") and w not in RANK:
            problems.append(f"weight must be must, standard or consider, not {f['Weight']!r}")
        report.append({"card": card["title"], "kind": "card", "ok": not problems,
                       "problems": problems, "warnings": warnings,
                       "clauses": [c for c, _ in cites]})
    return report


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    md = Path(sys.argv[1]).read_text()
    rep = check(md)
    if "--json" in sys.argv:
        print(json.dumps(rep, indent=1))
    else:
        for r in rep:
            mark = "PASS" if r["ok"] else "FAIL"
            print(f"[{mark}] {r['card']}")
            for p in r["problems"]:
                print(f"       x {p}")
            for w in r["warnings"]:
                print(f"       ! {w}")
        cards = [r for r in rep if r["kind"] == "card"]
        sugg = [r for r in rep if r["kind"] == "suggestion"]
        print(f"\n{sum(r['ok'] for r in cards)} of {len(cards)} cards pass.")
        if sugg:
            print(f"{sum(r['ok'] for r in sugg)} of {len(sugg)} suggestions pass.")
    return 0 if all(r["ok"] for r in rep) else 1


if __name__ == "__main__":
    sys.exit(main())
