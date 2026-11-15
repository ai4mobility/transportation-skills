"""Tests for the skill's code: the SOP rules and the card checker.

Run (from the repository root):  python -m pytest -q skills/d7-signal-sop/evals
"""
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FIX = SKILL / "evals" / "fixtures"
sys.path.insert(0, str(SKILL / "scripts"))

import check_cards  # noqa: E402
import rules  # noqa: E402


def test_clause_index():
    clauses = json.loads((SKILL / "references/clauses.json").read_text())["clauses"]
    by_id = {c["id"]: c for c in clauses}
    assert len(clauses) == 150
    assert by_id["TWO > Emergency TWOs > 12"]["weight"] == "must"
    assert by_id["Pre-Storm > One Week Prior > 7.1"]["weight"] == "consider"
    assert by_id["Post-Storm > Immediately Post Storm > 3.2.1"]["text"].startswith("First refueling")
    weights = [c["weight"] for c in clauses]
    assert (weights.count("must"), weights.count("standard"), weights.count("consider")) == (18, 123, 9)


def test_rules():
    assert rules.first_refuel("2026-10-10 06:10")["first_refuel"] == "2026-10-10 12:10"
    assert rules.first_refuel("2026-10-10 06:40")["first_refuel"] == "2026-10-10 12:40"
    assert rules.sat_passes("2026-10-10 07:30", "2026-10-11 09:00")["passes"] == [
        "2026-10-10 09:00", "2026-10-10 14:00", "2026-10-11 09:00"]
    assert rules.crew_notice_ok("2026-10-08 20:00", "2026-10-09 01:00")["ok"] is False
    assert rules.crew_notice_ok("2026-10-08 19:00", "2026-10-09 01:00")["ok"] is True
    assert rules.encumber_by("2026-10-20 15:00")["encumber_by"] == "2026-10-21 15:00"
    assert rules.emergency_two_allowed("2026-11-09", "2026-11-08", True, True)["allowed"] is False
    assert rules.emergency_two_allowed("2026-11-07", "2026-11-08", True, True)["allowed"] is True
    assert rules.emergency_two_allowed("2026-11-07", "2026-11-08", False, True)["allowed"] is False
    assert rules.cost_bucket(5000)["bucket"] == ">= $5,000"
    assert rules.cost_bucket(4999.99)["bucket"] == "< $5,000"
    assert "error" in rules.atms_status("blue")


def test_ddir_groups_on_synthetic_repairs():
    g = rules.ddir_candidates(rules.read_repairs(str(FIX / "repairs_synthetic.csv")))["groups"]
    by = {tuple(x["repairs"]): x for x in g}
    assert by[("R1", "R2")]["total"] == 5600 and by[("R1", "R2")]["needs_ddir"]
    assert by[("R3", "R4")]["total"] == 5000 and "exactly $5,000" in by[("R3", "R4")]["flags"][0]
    assert by[("R6", "R7", "R8")]["flags"] and "spans" in by[("R6", "R7", "R8")]["flags"][0]
    assert by[("R5",)]["needs_ddir"] is False
    assert sum(x["needs_ddir"] for x in g) == 3


def test_checker_passes_example_and_catches_bad_cards():
    good = check_cards.check((FIX / "example_cards.md").read_text())
    assert len(good) == 9 and all(r["ok"] for r in good)
    bad = check_cards.check((FIX / "bad_cards_synthetic.md").read_text())
    msgs = [" ".join(r["problems"]) for r in bad]
    assert not any(r["ok"] for r in bad)
    assert "not the SOP's words" in msgs[0]
    assert "weight raised" in msgs[1]
    assert "Appendix B" in msgs[2]
    assert "missing field: Who" in msgs[3] and "not in the SOP" in msgs[3]


def test_checker_keeps_experience_apart_from_the_sop():
    good = check_cards.check((FIX / "example_experience.md").read_text())
    assert [r["kind"] for r in good] == ["card", "card", "suggestion", "suggestion"]
    assert all(r["ok"] for r in good)
    bad = check_cards.check((FIX / "bad_suggestions_synthetic.md").read_text())
    msgs = [" ".join(r["problems"]) for r in bad]
    assert not any(r["ok"] for r in bad)
    assert "leaves the decision to a person" in msgs[0]
    assert "L9 is not in" in msgs[1]
    assert "not the SOP" in msgs[2]
    assert "clause not in the SOP: L1" in msgs[3]


def test_experience_files_are_labeled_and_sourced():
    refs = SKILL / "references"
    lessons = (refs / "lessons.md").read_text()
    blocks = re.split(r"(?m)^## (L\d+)\s*$", lessons)[1:]
    ids = blocks[0::2]
    assert ids == [f"L{i}" for i in range(1, 7)]
    for body in blocks[1::2]:
        assert "**Source:**" in body and "**Who decides:**" in body and "**Use when:**" in body
    assert "NOT the D7 SOP" in lessons and "NOT the D7 SOP" in (refs / "practice.md").read_text()
    assert set(ids) <= check_cards.experience_ids()          # practice entries may be added
    glossary = (refs / "glossary.md").read_text()
    assert len(re.findall(r"(?m)^\| [^|]+ \| [^|]+ \|$", glossary)) - 1 == 48   # minus the header
    skill = (SKILL / "SKILL.md").read_text()
    for f in refs.iterdir():
        assert f"references/{f.name}" in skill


def test_eval_expectations_match_the_code():
    """The numbers the evals expect must be what the skill's own rules return."""
    ev = json.loads((SKILL / "evals/evals.json").read_text())
    t1 = next(t for t in ev["tasks"] if t["id"] == "t1-day-one-cards")
    assert any("12:10" in e and "12:40" in e for e in t1["expectations"])
    t2 = next(t for t in ev["tasks"] if t["id"] == "t2-emergency-two-date")
    quote = re.search(r'"(Do not issue[^"]+)"', " ".join(t2["expectations"])).group(1)
    clauses = {c["id"]: c for c in json.loads((SKILL / "references/clauses.json").read_text())["clauses"]}
    assert quote == clauses["TWO > Emergency TWOs > 12"]["text"]
