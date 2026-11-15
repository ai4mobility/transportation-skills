"""Check journal-club review notes (the format in assets/review_notes.md) before handing
them over.

Run:
  python3 scripts/check_notes.py notes.md
  python3 scripts/check_notes.py notes.md --papers 2

Prints one PASS or FAIL line per check, then any warnings. Exit code 1 if any check fails.
It checks the form of the notes, not whether the reading is right: a person still reads
the paper.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import LIMITATIONS, STRENGTHS, VERDICTS  # noqa: E402

PARTS = (
    ("1", "Research problem"),
    ("2", "Contributions"),
    ("3", "Data and methods"),
    ("4", "Key results"),
    ("5", "Language and organization"),
    ("6", "Final evaluation and outlook"),
)
QUESTIONS = "Questions for the presenter"

# A place in the paper someone can check: p. 4, pp. 3-5, Sec. 3.2, Fig. 5, Table 2, Eq. 7,
# Appendix B, the abstract.
LOC_RE = re.compile(
    r"(\bpp?\.\s*\d|\bpages?\s+\d|\b(?:fig|figure|table|tab|sec|section|eq|equation|alg|algorithm)"
    r"s?\.?\s*[A-Z]?\d|\bappendix\s+[A-Z0-9]|\babstract\b|§\s*\d)",
    re.I,
)
# Saying the authors used AI. Checked only in part 5, so a paper that uses an LLM as a
# method can still be described in parts 3 and 4.
AI_CLAIM_RE = re.compile(
    r"(\b(?:written|generated|produced|drafted|composed)\s+(?:by|with|using)\s+(?:an?\s+)?"
    r"(?:ai|chatgpt|gpt[-\w]*|llms?|language models?|chatbots?)\b"
    r"|\bai[- ]generated\b|\bai[- ]written\b"
    r"|\b(?:authors?|they)\s+(?:\w+\s+){0,2}(?:used|relied\s+on|ran)\s+(?:an?\s+)?"
    r"(?:ai|chatgpt|gpt[-\w]*|llms?|language models?|chatbots?)\b"
    r"(?:\s+to\s+(?:write|draft|polish|generate))?)",
    re.I,
)
GENERIC_LIMIT_RE = re.compile(r"\b(more data|larger (?:data ?set|sample)|future work|further research)\b", re.I)
NOVELTY_OK_RE = re.compile(r"(not checked|https?://|\bdoi\b|\b10\.\d{4,}/)", re.I)


def sections(text: str) -> dict[str, str]:
    """'## <title>' -> its text, keyed by the lowercased title."""
    out: dict[str, str] = {}
    matches = list(re.finditer(r"(?m)^##[ \t]+(.+?)\s*$", text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[m.group(1).strip().lower()] = text[m.end():end]
    return out


def find_part(secs: dict[str, str], num: str, title: str) -> str | None:
    for key, body in secs.items():
        if re.match(rf"^{num}\.?\s+{re.escape(title.lower())}", key):
            return body
    return None


def table_rows(body: str) -> list[list[str]]:
    rows = []
    for line in body.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        if re.fullmatch(r"\|[\s:|-]+\|?", s):
            continue          # the |---|---| line
        cells = [c.strip() for c in s.strip("|").split("|")]
        rows.append(cells)
    return rows[1:] if rows else []      # drop the header row


def list_after(body: str, label: str) -> list[str] | None:
    """Bullets that follow a line starting with `label`, up to the next non-bullet line."""
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if re.match(rf"^\s*\**{label}\**\s*:?\s*\**\s*$", line, re.I):
            items = []
            for nxt in lines[i + 1:]:
                if re.match(r"^\s*[-*]\s+\S", nxt):
                    items.append(re.sub(r"^\s*[-*]\s+", "", nxt).strip())
                elif not nxt.strip():
                    if items:
                        break
                else:
                    break
            return items
    return None


def norm_verdict(cell: str) -> str:
    return re.sub(r"[*_`.]", "", cell).strip().lower()


def check(text: str, papers: int = 1) -> dict:
    """Return {"checks": [(name, ok, [problems])], "warnings": [...]}."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)     # comments are not part of the notes
    secs = sections(text)
    checks: list[tuple[str, bool, list[str]]] = []
    warnings: list[str] = []

    def add(name: str, problems: list[str]) -> None:
        checks.append((name, not problems, problems))

    # 1. All six parts and the questions section.
    parts = {num: find_part(secs, num, title) for num, title in PARTS}
    add("six parts present",
        [f"missing '## {num}. {title}'" for (num, title) in PARTS if parts[num] is None])
    q_body = next((b for k, b in secs.items() if k.startswith(QUESTIONS.lower())), None)

    # 2. Every "Paper says:" line points to a place in the paper.
    probs = []
    for line in text.split("\n"):
        if re.match(r"^\s*\**paper says\**\s*:", line, re.I) and not LOC_RE.search(line):
            probs.append(f"'Paper says' with no page, section, figure or table: {line.strip()[:70]}")
    if not re.search(r"(?im)^\s*\**paper says\**\s*:", text):
        probs.append("no 'Paper says:' lines; keep what the paper says apart from the assessment")
    add("paper says has a location", probs)

    # 3. The contribution table.
    probs = []
    body2 = parts.get("2") or ""
    rows = table_rows(body2)
    if not rows:
        probs.append("part 2 has no contribution table")
    for cells in rows:
        if len(cells) < 3:
            probs.append(f"table row needs claim | evidence | verdict: {' | '.join(cells)[:70]}")
            continue
        claim, evidence, verdict = cells[0], cells[1], cells[-1]
        if not LOC_RE.search(claim):
            probs.append(f"claimed contribution has no location: {claim[:60]}")
        if not evidence or evidence in ("-", "?"):
            probs.append(f"no evidence given for: {claim[:60]}")
        if norm_verdict(verdict) not in VERDICTS:
            probs.append(f"verdict '{verdict}' is not one of: {', '.join(VERDICTS)}")
    add("contribution table", probs)

    # 4. Novelty: a real link or DOI, or an honest "not checked".
    probs = []
    nov = [ln for ln in body2.split("\n") if re.match(r"^\s*\**novelty check\**\s*:", ln, re.I)]
    if not nov:
        probs.append("part 2 has no 'Novelty check:' line")
    elif not NOVELTY_OK_RE.search(" ".join(nov)):
        probs.append("'Novelty check' cites no DOI or link; cite papers you found, "
                     "or write 'novelty not checked'")
    add("novelty check", probs)

    # 5. 2-3 strengths and 2-3 limitations, each with a location.
    probs = []
    body6 = parts.get("6") or ""
    for label, (lo, hi) in (("Strengths", STRENGTHS), ("Limitations", LIMITATIONS)):
        items = list_after(body6, label)
        if items is None:
            probs.append(f"part 6 has no '{label}:' list")
            continue
        if not lo <= len(items) <= hi:
            probs.append(f"{len(items)} {label.lower()}; the guide asks for {lo}-{hi}")
        for it in items:
            if not LOC_RE.search(it):
                probs.append(f"{label[:-1].lower()} with no location: {it[:60]}")
            if label == "Limitations" and GENERIC_LIMIT_RE.search(it) and not re.search(r"\d", it):
                warnings.append(f"limitation may be too general to be useful: {it[:60]}")
    add("strengths and limitations", probs)

    # 6. Every presenter's call carries a labeled draft view, and is listed as a question.
    probs = []
    lines = text.split("\n")
    q_start = text.lower().find("## " + QUESTIONS.lower())
    calls = 0
    offset = 0
    for i, line in enumerate(lines):
        here = offset
        offset += len(line) + 1
        if "[presenter's call]" not in line.lower():
            continue
        if q_start != -1 and here > q_start:
            continue
        calls += 1
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if "draft view" not in (line + " " + nxt).lower():
            probs.append(f"[Presenter's call] without a 'Draft view': {line.strip()[:60]}")
    if calls == 0:
        probs.append("no [Presenter's call] items; the guide asks for the presenter's opinion "
                     "on importance, validity and the takeaway")
    if q_body is None:
        probs.append(f"missing '## {QUESTIONS}'")
    else:
        n_q = len(re.findall(r"(?m)^\s*(?:\d+[.)]|[-*])\s+\S", q_body))
        if n_q == 0:
            probs.append(f"'## {QUESTIONS}' is empty")
        elif n_q < calls:
            warnings.append(f"{calls} presenter's calls but {n_q} questions for the presenter")
    add("presenter's calls", probs)

    # 7. Style observations only: never say the authors used AI.
    probs = []
    body5 = parts.get("5") or ""
    for m in AI_CLAIM_RE.finditer(body5):
        probs.append(f"part 5 says the authors used AI ('{m.group(0)}'); "
                     "report the style only")
    add("no claim that the authors used AI", probs)

    # 8. Two or more papers: the comparison.
    if papers > 1:
        probs = []
        comp = next((b for k, b in secs.items() if k.startswith("comparison")), None)
        if comp is None:
            probs.append("two or more papers but no '## Comparison' section")
        else:
            if not table_rows(comp):
                probs.append("'## Comparison' has no table")
            if not re.search(r"\b(complementary|overlapping|conflicting)\b", comp, re.I):
                probs.append("say whether the conclusions are complementary, overlapping or "
                             "conflicting")
        add("comparison of papers", probs)

    return {"checks": checks, "warnings": warnings}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("notes")
    ap.add_argument("--papers", type=int, default=1)
    args = ap.parse_args(argv)
    result = check(Path(args.notes).read_text(), args.papers)
    for name, ok, probs in result["checks"]:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        for p in probs:
            print(f"      - {p}")
    for w in result["warnings"]:
        print(f"WARN  {w}")
    return 0 if all(ok for _, ok, _ in result["checks"]) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
