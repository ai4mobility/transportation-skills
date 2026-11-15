"""Run a skill's evals with and without the skill, so you can grade the answers by hand.

What it does, for the skill folder you give it:
  1. Load tests: each request in should_load and should_not_load, once, with the skill
     installed. Records whether the agent opened the skill (Claude Code only; for other
     agents, read the transcript).
  2. Tasks: each task with the skill and without it, --runs times each (default 3), every
     run in a fresh, empty workspace that holds only the task's files.
  3. Writes evals/runs/<date-time>/: every answer, every transcript, and answers.md, a sheet
     you grade by hand (right / partly / wrong, and why). Copy the counts into RESULTS.md.

The model never sees evals/: only the skill's other files are copied into a workspace, and
workspaces live in a temporary folder outside this repository.

Clients:
  --client claude          Claude Code in print mode (claude -p). Install Claude Code and log
                           in first. --model picks the model; write it down in RESULTS.md.
  --client cmd --cmd "..." any command-line agent. Placeholders: {workspace}, {prompt_file},
                           {prompt} (already shell-quoted). For 'with' runs the skill is in
                           {workspace}/.claude/skills/<name>/ and {workspace}/.agents/skills/<name>/.
  --client manual          no agent: writes manual_sheet.md, steps for doing the same runs by
                           hand in claude.ai (skill on, skill off), and an empty answers.md.

Examples (from the repository root):
  python tools/run_evals.py skills/d7-signal-sop --client claude --runs 3
  python tools/run_evals.py skills/d7-signal-sop --client claude --tasks t1 --runs 1 --no-load-tests
  python tools/run_evals.py skills/d7-signal-sop --client manual
"""
from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# What the agent may do inside the throwaway workspace: read, write its answer, run python.
CLAUDE_TOOLS = "Read Write Edit Glob Grep Skill Bash(python3 *) Bash(python *)"
SKIP = shutil.ignore_patterns("evals", "__pycache__", "*.pyc", ".DS_Store")


def make_workspace(base: Path, label: str, skill: Path, with_skill: bool, files: list[str]) -> Path:
    ws = base / label
    ws.mkdir(parents=True)
    for f in files:
        shutil.copy(skill / "evals" / f, ws / Path(f).name)
    if with_skill:
        for loc in (".claude/skills", ".agents/skills"):
            shutil.copytree(skill, ws / loc / skill.name, ignore=SKIP)
    return ws


def parse_claude_stream(text: str, skill_name: str) -> tuple[str, bool, list[str]]:
    """Final answer, whether the skill was opened, and the tools used, from stream-json."""
    answer, last_text, loaded, tools = "", "", False, []
    for line in text.splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "result" and isinstance(ev.get("result"), str):
            answer = ev["result"]
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
        for block in msg.get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and ev.get("type") == "assistant":
                last_text = block.get("text", "")
            if block.get("type") == "tool_use":
                name = block.get("name", "")
                inp = json.dumps(block.get("input", {}))
                tools.append(name)
                if (name == "Skill" and skill_name in inp) or f"skills/{skill_name}/SKILL.md" in inp:
                    loaded = True
    return answer or last_text, loaded, tools


def run_one(args, skill: Path, ws: Path, prompt: str, prompt_file: Path) -> dict:
    prompt_file.write_text(prompt)
    if args.client == "claude":
        cmd = ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
               "--max-turns", str(args.max_turns), "--allowedTools", CLAUDE_TOOLS]
        if args.model:
            cmd += ["--model", args.model]
    else:
        cmd = args.cmd.format(workspace=shlex.quote(str(ws)), prompt_file=shlex.quote(str(prompt_file)),
                              prompt=shlex.quote(prompt))
    try:
        p = subprocess.run(cmd, cwd=ws, capture_output=True, text=True, timeout=args.timeout,
                           shell=isinstance(cmd, str))
        raw, err, code = p.stdout, p.stderr, p.returncode
    except FileNotFoundError:
        sys.exit("Claude Code was not found. Install it and log in (claude), or use --client cmd/manual.")
    except subprocess.TimeoutExpired as e:
        partial = e.stdout
        raw = partial.decode(errors="ignore") if isinstance(partial, bytes) else (partial or "")
        err, code = f"timed out after {args.timeout} s", -1
    if args.client == "claude":
        answer, loaded, tools = parse_claude_stream(raw, skill.name)
    else:
        answer, loaded, tools = raw.strip(), None, []
    return {"answer": answer, "loaded": loaded, "tools": tools, "raw": raw, "stderr": err, "code": code}


def write_manual(skill: Path, data: dict, out: Path, runs: int) -> None:
    name = skill.name
    lines = [f"# Manual eval sheet: {name} (claude.ai)", "",
             "Do every run in a **new chat**, so one answer cannot shape the next.", "",
             "## Set up once", "",
             f"1. Make the zip: `python tools/package_skills.py skills/{name}` (it leaves evals/ out).",
             f"2. In claude.ai: Customize > Skills > Upload a skill > `dist/{name}.zip`.",
             "3. Write down the model you use (it is shown under the chat box).", "",
             "## Load tests (skill ON)", "",
             "Paste each request in a new chat. Claude shows a step when it opens a skill; "
             "write yes if it opened this one.", "",
             "| # | Request | Should load | Loaded? |", "|---|---|---|---|"]
    for i, q in enumerate(data["should_load"] + data["should_not_load"], 1):
        should = "yes" if q in data["should_load"] else "no"
        lines.append(f"| {i} | {q.replace('|', '/')} | {should} | |")
    lines += ["", "## Tasks", "",
              f"Each task {runs} times with the skill ON, then {runs} times with it OFF "
              "(Customize > Skills, switch it off). Paste every answer into answers.md.", ""]
    for t in data["tasks"]:
        files = ", ".join(f"`evals/{f}`" for f in t.get("files", []) or []) or "none"
        lines += [f"### {t['id']}", "", f"Attach: {files}", "", "Prompt:", "", f"> {t['prompt']}", ""]
    (out / "manual_sheet.md").write_text("\n".join(lines) + "\n")


def write_answers(skill: Path, data: dict, results: list[dict], load: list[dict], out: Path,
                  meta: dict) -> None:
    lines = [f"# Answers to grade: {skill.name}", "",
             f"Client: {meta['client']} · model: {meta['model'] or 'default'} · runs: {meta['runs']} · "
             f"{meta['started']}", "",
             "Grade each answer **right / partly / wrong** against the task's expectations, and say "
             "why in a few words. Then copy the counts into `evals/RESULTS.md`.", ""]
    if load:
        sl = [x for x in load if x["should"]]
        sn = [x for x in load if not x["should"]]
        known = all(x["loaded"] is not None for x in load)
        lines += ["## Load tests", ""]
        if known:
            lines += [f"Should load: {sum(x['loaded'] for x in sl)} of {len(sl)} loaded. "
                      f"Should not load: {sum(x['loaded'] for x in sn)} of {len(sn)} loaded.", ""]
        lines += ["| Request | Should load | Loaded |", "|---|---|---|"]
        for x in load:
            got = "?" if x["loaded"] is None else ("yes" if x["loaded"] else "no")
            lines.append(f"| {x['prompt'].replace('|', '/')} | {'yes' if x['should'] else 'no'} | {got} |")
        lines.append("")
    for t in data["tasks"]:
        lines += [f"## {t['id']}", "", f"**Prompt:** {t['prompt']}", "", "**Expectations:**", ""]
        lines += [f"- {e}" for e in t["expectations"]] + [""]
        for r in [r for r in results if r["task"] == t["id"]]:
            flag = ""
            if r["setup"] == "without" and r.get("loaded"):
                flag = "  ⚠ the skill was opened in a 'without' run: another copy is installed; this run does not count"
            lines += [f"### {t['id']} · {r['setup']} skill · run {r['run']}{flag}", "",
                      f"File: `{r['file']}`", "", r["answer"].strip() or "_(empty answer)_", "",
                      "**Grade:** ", "", "**Why:** ", ""]
    (out / "answers.md").write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("skill", type=Path)
    ap.add_argument("--client", choices=["claude", "cmd", "manual"], required=True)
    ap.add_argument("--cmd", help="command for --client cmd")
    ap.add_argument("--model")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--tasks", help="comma-separated task ids (default: all)")
    ap.add_argument("--no-load-tests", action="store_true")
    ap.add_argument("--max-turns", type=int, default=30)
    ap.add_argument("--timeout", type=int, default=600, help="seconds per run")
    args = ap.parse_args()
    if args.client == "cmd" and not args.cmd:
        ap.error("--client cmd needs --cmd")

    skill = args.skill.resolve()
    data = json.loads((skill / "evals" / "evals.json").read_text())
    tasks = data["tasks"]
    if args.tasks:
        keep = set(args.tasks.split(","))
        tasks = [t for t in tasks if t["id"] in keep]
    started = datetime.now().strftime("%Y-%m-%d %H:%M")
    out = skill / "evals" / "runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True)
    meta = {"client": args.client, "model": args.model, "runs": args.runs, "started": started}

    if args.client == "manual":
        write_manual(skill, {**data, "tasks": tasks}, out, args.runs)
        fake = [{"task": t["id"], "setup": s, "run": n, "file": "(paste here)", "answer": ""}
                for t in tasks for s in ("with", "without") for n in range(1, args.runs + 1)]
        write_answers(skill, {**data, "tasks": tasks}, fake, [], out, meta)
        print(f"wrote {out / 'manual_sheet.md'} and {out / 'answers.md'}")
        return 0

    base = Path(tempfile.mkdtemp(prefix=f"evals-{skill.name}-"))
    load: list[dict] = []
    if not args.no_load_tests:
        for i, q in enumerate(data["should_load"] + data["should_not_load"], 1):
            ws = make_workspace(base, f"load{i}", skill, True, [])
            r = run_one(args, skill, ws, q, base / f"load{i}.prompt.txt")
            should = q in data["should_load"]
            load.append({"prompt": q, "should": should, "loaded": r["loaded"]})
            got = "?" if r["loaded"] is None else ("loaded" if r["loaded"] else "not loaded")
            print(f"[load] {'should' if should else 'should not'} load -> {got}: {q[:60]}")
            (out / f"load{i}.jsonl").write_text(r["raw"])

    results: list[dict] = []
    for t in tasks:
        for setup in ("with", "without"):
            for n in range(1, args.runs + 1):
                label = f"{t['id']}__{setup}__run{n}"
                ws = make_workspace(base, label, skill, setup == "with", t.get("files", []) or [])
                r = run_one(args, skill, ws, t["prompt"], base / f"{label}.prompt.txt")
                (out / f"{label}.md").write_text(r["answer"] + "\n")
                (out / f"{label}.transcript.txt").write_text(r["raw"] + ("\n--- stderr ---\n" + r["stderr"]
                                                                           if r["stderr"] else ""))
                results.append({"task": t["id"], "setup": setup, "run": n, "file": f"{label}.md",
                                "answer": r["answer"], "loaded": r["loaded"], "code": r["code"]})
                note = "" if r["code"] == 0 else f" (exit {r['code']})"
                print(f"[task] {label}{note}")

    write_answers(skill, {**data, "tasks": tasks}, results, load, out, meta)
    (out / "summary.json").write_text(json.dumps({"meta": meta, "load_tests": load,
                                                  "runs": [{k: v for k, v in r.items() if k != "answer"}
                                                           for r in results]}, indent=1))
    shutil.rmtree(base, ignore_errors=True)
    print(f"\nGrade the answers in {out / 'answers.md'}, then write evals/RESULTS.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
