"""Tests for the repository's tools: the checker, the packager, the catalog and the eval runner.

Run (from the repository root):  python -m pytest -q tests
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_catalog  # noqa: E402
import check_skill  # noqa: E402
import package_skills  # noqa: E402
import run_evals  # noqa: E402

D7 = ROOT / "skills" / "d7-signal-sop"


def copy_d7(tmp_path, name="d7-signal-sop"):
    dst = tmp_path / name
    shutil.copytree(D7, dst, ignore=shutil.ignore_patterns("__pycache__", "runs"))
    return dst


def errors(folder):
    return " | ".join(check_skill.check_skill(folder).errors)


def edit(path, old, new):
    s = path.read_text()
    assert s.count(old) == 1, f"{old!r} found {s.count(old)} times"
    path.write_text(s.replace(old, new))


# --- the checker ---------------------------------------------------------------------

def test_every_skill_in_the_repository_passes():
    for folder in sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir()):
        rep = check_skill.check_skill(folder)
        assert rep.ok, f"{folder.name}: {rep.errors}"


def test_the_template_fails_until_filled_in():
    e = errors(ROOT / "template" / "new-skill")
    assert "SKILL.md still has TODO" in e and "evals/evals.json still has TODO" in e
    assert "metadata domain" in e


@pytest.mark.parametrize("old,new,expected", [
    ("name: d7-signal-sop", "name: D7-Signal-SOP", "lowercase letters"),
    ("name: d7-signal-sop", "name: d7--signal-sop", "single hyphens"),
    ("name: d7-signal-sop", "name: d7-signal", "must match the folder name"),
    ("license: MIT", "license: MIT\nversion: 1.0", "not in the open format"),
    ('status: "draft"', 'status: "final"', "status must be one of"),
    ('status: "draft"', 'status: "reviewed"', "needs metadata 'reviewed-by'"),
    ('status: "draft"', 'status: "tested"', "needs evals/RESULTS.md"),
    ('domain: "emergency-response"', 'domain: "hurricanes"', "metadata domain"),
    ('version: "1.0.0"', 'version: "v1"', "version must look like"),
    ('version: "1.0.0"', "version: 1.0", "must be text"),
    ('sources-checked: "2026-11-13"', 'sources-checked: "Nov 13"', "must be a date"),
    ("## Sources", "## Where it came from", "needs a '## Sources' section"),
    ("## Limits", "## Caveats", "needs a '## Limits' section"),
    ("Reuse: public agency document;", "public agency document;", "no 'Reuse:' note"),
    ("`assets/action_card.md`: the card", "`assets/card_format.md`: the card", "assets/card_format.md, which does not exist"),
])
def test_checker_catches_each_problem(tmp_path, old, new, expected):
    f = copy_d7(tmp_path)
    edit(f / "SKILL.md", old, new)
    assert expected in errors(f)


def test_description_rules(tmp_path):
    f = copy_d7(tmp_path)
    sk = f / "SKILL.md"
    text = sk.read_text()
    desc = re.search(r"(?m)^description: (.*)$", text).group(1)
    sk.write_text(text.replace(desc, desc + " See <the SOP>."))
    assert "cannot contain '<' or '>'" in errors(f)
    sk.write_text(text.replace(desc, "x" * 1025))
    assert "the limit is 1,024" in errors(f)
    sk.write_text(text.replace("name: d7-signal-sop", "name: claude-d7"))
    g = tmp_path / "claude-d7"
    f.rename(g)
    assert "contains 'claude'" in errors(g)


def test_evals_rules(tmp_path):
    f = copy_d7(tmp_path)
    ev = f / "evals" / "evals.json"
    data = json.loads(ev.read_text())
    data["should_not_load"] = data["should_not_load"][:2]
    data["tasks"][0]["files"] = ["files/missing.md"]
    ev.write_text(json.dumps(data))
    e = errors(f)
    assert "at least 3 'should_not_load'" in e and "files/missing.md does not exist" in e
    ev.unlink()
    assert "missing evals/evals.json" in errors(f)


def test_scripts_need_tests_and_files_need_care(tmp_path):
    f = copy_d7(tmp_path)
    (f / "evals" / "test_scripts.py").unlink()
    assert "every rule in code needs a test" in errors(f)
    f = copy_d7(tmp_path / "b")
    (f / "references" / "notes.md").write_text("key: sk-ant-" + "a" * 40 + "\n")
    (f / ".env").write_text("X=1\n")
    e = errors(f)
    assert "an Anthropic API key" in e and "looks like a secrets file" in e


def test_source_documents_stay_out(tmp_path):
    f = copy_d7(tmp_path)
    (f / "references" / "D7_Signal_SOP_v1.5.pdf").write_bytes(b"%PDF-1.7 synthetic")
    assert "is a document file" in errors(f)


def test_body_length_limit(tmp_path):
    f = copy_d7(tmp_path)
    with (f / "SKILL.md").open("a") as fh:
        fh.write("\n".join(f"- line {i}" for i in range(600)))
    assert "keep it under 500" in errors(f)


def test_pull_request_scope_rule():
    one = ["skills/a/SKILL.md", "skills/a/evals/evals.json"]
    assert check_skill.pr_scope_problems(one) == []
    assert check_skill.pr_scope_problems(["tools/check_skill.py", "README.md"]) == []
    two = check_skill.pr_scope_problems(["skills/a/SKILL.md", "skills/b/SKILL.md"])
    assert "more than one skill" in two[0]
    mixed = check_skill.pr_scope_problems(["skills/a/SKILL.md", "tools/check_skill.py"])
    assert "only skills/<name>/" in mixed[0]


# --- the packager ----------------------------------------------------------------------

def test_package_leaves_evals_out(tmp_path):
    z = package_skills.package(D7, tmp_path)
    names = zipfile.ZipFile(z).namelist()
    assert "d7-signal-sop/SKILL.md" in names
    assert "d7-signal-sop/scripts/check_cards.py" in names
    assert not any("/evals/" in n or "__pycache__" in n for n in names)


# --- the catalog -----------------------------------------------------------------------

def test_catalog_lists_every_skill_and_is_current():
    rows = build_catalog.collect()
    assert [r["name"] for r in rows] == sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert "d7-signal-sop" in build_catalog.table(rows)
    assert build_catalog.main(["--check"]) == 0, "run python tools/build_catalog.py"


# --- the eval runner -------------------------------------------------------------------

def test_workspace_never_holds_evals(tmp_path):
    ws = run_evals.make_workspace(tmp_path, "w", D7, True, ["files/scenario_day1.md"])
    assert (ws / "scenario_day1.md").exists()
    for loc in (".claude/skills", ".agents/skills"):
        assert (ws / loc / "d7-signal-sop" / "SKILL.md").exists()
        assert not (ws / loc / "d7-signal-sop" / "evals").exists()
    bare = run_evals.make_workspace(tmp_path, "wo", D7, False, [])
    assert list(bare.iterdir()) == []


def test_parse_claude_stream_finds_the_skill_and_the_answer():
    lines = [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "d7-signal-sop"}}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "### Card 1 ..."}]}},
        {"type": "result", "subtype": "success", "result": "### Card 1 ...final"},
    ]
    answer, loaded, tools = run_evals.parse_claude_stream("\n".join(map(json.dumps, lines)), "d7-signal-sop")
    assert answer.endswith("final") and loaded and tools == ["Skill"]
    lines[1]["message"]["content"][0] = {"type": "tool_use", "name": "Read",
                                         "input": {"file_path": "/w/.claude/skills/d7-signal-sop/SKILL.md"}}
    assert run_evals.parse_claude_stream("\n".join(map(json.dumps, lines)), "d7-signal-sop")[1]
    lines[1]["message"]["content"][0] = {"type": "tool_use", "name": "Read", "input": {"file_path": "x.md"}}
    assert not run_evals.parse_claude_stream("\n".join(map(json.dumps, lines)), "d7-signal-sop")[1]


def test_run_evals_end_to_end_with_a_stand_in_agent(tmp_path):
    """A stand-in agent lists its workspace; the 'with' runs must see the skill, never evals/."""
    skill = copy_d7(tmp_path)
    agent = ("python3 -c \"import os,sys; ws=sys.argv[1]; "
             "print(sorted(os.path.relpath(os.path.join(d,f),ws) for d,_,fs in os.walk(ws) for f in fs))\" {workspace}")
    cmd = [sys.executable, str(ROOT / "tools" / "run_evals.py"), str(skill), "--client", "cmd",
           "--cmd", agent, "--runs", "1", "--tasks", "t1-day-one-cards", "--no-load-tests"]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    run = sorted((skill / "evals" / "runs").iterdir())[-1]
    with_ans = (run / "t1-day-one-cards__with__run1.md").read_text()
    without_ans = (run / "t1-day-one-cards__without__run1.md").read_text()
    assert ".claude/skills/d7-signal-sop/SKILL.md" in with_ans and "scenario_day1.md" in with_ans
    assert "evals" not in with_ans
    assert "SKILL.md" not in without_ans and "scenario_day1.md" in without_ans
    answers = (run / "answers.md").read_text()
    assert answers.count("**Grade:**") == 2 and "12:10" in answers


def test_manual_sheet(tmp_path):
    skill = copy_d7(tmp_path)
    cmd = [sys.executable, str(ROOT / "tools" / "run_evals.py"), str(skill), "--client", "manual"]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr
    run = sorted((skill / "evals" / "runs").iterdir())[-1]
    sheet = (run / "manual_sheet.md").read_text()
    assert "Upload a skill" in sheet and sheet.count("| no |") == 4
    assert (run / "answers.md").read_text().count("**Grade:**") == 3 * 2 * 3
