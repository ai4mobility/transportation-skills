"""Rebuild the skill catalog: the table in README.md and catalog.json.

The workflow .github/workflows/catalog.yml runs this after every merge to main, so a
contributor never edits README.md for a new skill.

Run (from the repository root):
  python tools/build_catalog.py           rewrite README.md and catalog.json
  python tools/build_catalog.py --check   exit 1 if either is out of date
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_skill import ROOT, SKILLS, split_frontmatter  # noqa: E402

README = ROOT / "README.md"
CATALOG = ROOT / "catalog.json"
START, END = "<!-- catalog:start -->", "<!-- catalog:end -->"
BADGE = {"draft": "draft", "tested": "tested", "reviewed": "**reviewed**"}


def first_sentence(text: str, limit: int = 170) -> str:
    s = re.split(r"(?<=[.!?])\s", text.strip(), maxsplit=1)[0]
    return s if len(s) <= limit else s[: limit - 1].rstrip() + "…"


def collect() -> list[dict]:
    rows = []
    for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir()) if SKILLS.is_dir() else []:
        sk = folder / "SKILL.md"
        if not sk.exists():
            continue
        fm, _, problem = split_frontmatter(sk.read_text())
        if problem or not fm:
            continue
        md = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
        rows.append({
            "name": fm.get("name", folder.name),
            "summary": first_sentence(str(fm.get("description", ""))),
            "domain": md.get("domain", ""),
            "status": md.get("status", ""),
            "version": md.get("version", ""),
            "authors": md.get("authors", ""),
            "path": f"skills/{folder.name}",
        })
    return rows


def table(rows: list[dict]) -> str:
    if not rows:
        return "_No skills yet. Yours could be the first: see [CONTRIBUTING.md](CONTRIBUTING.md)._"
    out = ["| Skill | What it does | Domain | Status | Version |", "|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| [`{r['name']}`]({r['path']}/SKILL.md) | {r['summary'].replace('|', '/')} | "
                   f"{r['domain']} | {BADGE.get(r['status'], r['status'])} | {r['version']} |")
    return "\n".join(out)


def render_readme(rows: list[dict]) -> str:
    text = README.read_text()
    if START not in text or END not in text:
        raise SystemExit(f"README.md needs the two marker lines {START} and {END}")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    return f"{head}{START}\n{table(rows)}\n{END}{tail}"


def main(argv: list[str]) -> int:
    rows = collect()
    new_readme = render_readme(rows)
    new_catalog = json.dumps({"skills": rows}, indent=2) + "\n"
    if "--check" in argv:
        stale = []
        if README.read_text() != new_readme:
            stale.append("README.md")
        if not CATALOG.exists() or CATALOG.read_text() != new_catalog:
            stale.append("catalog.json")
        if stale:
            print("out of date: " + ", ".join(stale) + " (run python tools/build_catalog.py)")
            return 1
        print(f"catalog is current ({len(rows)} skills)")
        return 0
    README.write_text(new_readme)
    CATALOG.write_text(new_catalog)
    print(f"catalog written: {len(rows)} skill(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
