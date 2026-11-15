"""Tests for the skill's code: the guide's numbers, the slide budget, and the notes checker.

Run (from the repository root):  python -m pytest -q skills/journal-club-paper-review/evals
"""
import subprocess
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
FIX = SKILL / "evals" / "fixtures"
sys.path.insert(0, str(SKILL / "scripts"))

import check_notes  # noqa: E402
import rules  # noqa: E402


def counts(budget):
    return {s["part"]: s["count"] for s in budget["slides"]}


def test_numbers_from_the_guide():
    assert rules.STRENGTHS == (2, 3)
    assert rules.LIMITATIONS == (2, 3)
    assert rules.VERDICTS == ("supported", "partly supported", "not shown")


def test_slide_budget():
    b20 = rules.slide_budget(20)
    assert b20["total"] == 10 == sum(counts(b20).values())
    c = counts(b20)
    assert c["title"] == 1 and c["contributions"] == 1 and c["results"] == 2
    assert "comparison" not in c and "discussion" not in c
    assert [s["part"] for s in b20["slides"]][0] == "title"

    b10 = rules.slide_budget(10)
    assert b10["total"] == 5
    assert set(counts(b10)) == {"title", "problem", "contributions", "methods", "results"}
    assert "gap and scope go on the problem slide" in b10["note"]

    b30 = rules.slide_budget(30, papers=2)
    c = counts(b30)
    assert b30["total"] == 15 and c["comparison"] == 2 and c["discussion"] == 1
    assert c["results"] + c["methods"] + c["contributions"] >= 6      # most time on parts 2-4

    b60 = rules.slide_budget(60)
    assert b60["total"] == 30 == sum(counts(b60).values())

    assert "error" in rules.slide_budget(3)
    assert "error" in rules.slide_budget(20, papers=0)


def test_cli():
    out = subprocess.run([sys.executable, str(SKILL / "scripts/rules.py"), "slides", "20"],
                         capture_output=True, text=True)
    assert out.returncode == 0 and '"total": 10' in out.stdout
    bad = subprocess.run([sys.executable, str(SKILL / "scripts/check_notes.py"),
                          str(FIX / "bad_notes_synthetic.md")], capture_output=True, text=True)
    assert bad.returncode == 1 and "FAIL" in bad.stdout


def test_good_notes_pass():
    r = check_notes.check((FIX / "good_notes_synthetic.md").read_text())
    failed = [(n, p) for n, ok, p in r["checks"] if not ok]
    assert not failed, failed
    assert len(r["checks"]) == 7


def test_every_planted_mistake_is_caught():
    r = check_notes.check((FIX / "bad_notes_synthetic.md").read_text())
    msgs = " ".join(p for _, _, probs in r["checks"] for p in probs)
    assert "'Paper says' with no page" in msgs                       # M1
    assert "[Presenter's call] without a 'Draft view'" in msgs        # M2
    assert "verdict 'valid' is not one of" in msgs                    # M3
    assert "claimed contribution has no location" in msgs             # M4
    assert "'Novelty check' cites no DOI or link" in msgs             # M5
    assert "missing '## 4. Key results'" in msgs                      # M6
    assert "says the authors used AI" in msgs                         # M7
    assert "4 strengths; the guide asks for 2-3" in msgs              # M8
    assert "limitation with no location" in msgs                      # M8
    assert any("too general" in w for w in r["warnings"])


def test_method_that_uses_an_llm_is_not_flagged():
    # A paper whose METHOD uses an LLM can be described in part 3; only part 5 is checked.
    text = (FIX / "good_notes_synthetic.md").read_text().replace(
        "Pipeline: demand", "Paper says: the authors used an LLM to label crash narratives (Sec. 3).\nPipeline: demand")
    r = check_notes.check(text)
    assert all(ok for _, ok, _ in r["checks"])


def test_two_papers_need_a_comparison():
    good = (FIX / "good_notes_synthetic.md").read_text()
    r = check_notes.check(good, papers=2)
    msgs = " ".join(p for _, _, probs in r["checks"] for p in probs)
    assert "no '## Comparison' section" in msgs
    with_comp = good + (
        "\n## Comparison\n| | Paper A | Paper B |\n|---|---|---|\n| Data | SUMO | field |\n\n"
        "The conclusions are complementary, because one is simulated and one is observed.\n")
    r = check_notes.check(with_comp, papers=2)
    assert all(ok for _, ok, _ in r["checks"])
