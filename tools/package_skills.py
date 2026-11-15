"""Zip skills for upload to claude.ai (Customize > Skills > Upload a skill) or any client
that takes a skill as a zip.

Each zip holds one folder, <name>/, with SKILL.md at its top. The evals/ folder is left
out on purpose: the model never needs it, and the expected answers in evals.json must
not be visible to a model that is being tested.

Run (from the repository root):
  python tools/package_skills.py                       every skill -> dist/<name>.zip
  python tools/package_skills.py skills/d7-signal-sop  one skill
  python tools/package_skills.py --status reviewed     only reviewed skills
  python tools/package_skills.py --out somewhere/
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_skill import ROOT, SKILLS, check_skill, split_frontmatter  # noqa: E402

LEAVE_OUT_DIRS = {"evals", "__pycache__", ".git", ".pytest_cache"}
LEAVE_OUT_FILES = {".DS_Store", "Thumbs.db"}


def skill_status(folder: Path) -> str | None:
    fm, _, _ = split_frontmatter((folder / "SKILL.md").read_text())
    md = (fm or {}).get("metadata") or {}
    return md.get("status") if isinstance(md, dict) else None


def files_to_pack(folder: Path) -> list[Path]:
    out = []
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder)
        if p.is_dir() or rel.parts[0] in LEAVE_OUT_DIRS or set(rel.parts) & LEAVE_OUT_DIRS:
            continue
        if p.name in LEAVE_OUT_FILES or p.suffix == ".pyc":
            continue
        out.append(p)
    return out


def package(folder: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{folder.name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files_to_pack(folder):
            z.write(p, f"{folder.name}/{p.relative_to(folder).as_posix()}")
    with zipfile.ZipFile(target) as z:
        names = z.namelist()
    assert f"{folder.name}/SKILL.md" in names, "SKILL.md must be at the top of the skill folder"
    assert not any("/evals/" in n for n in names), "evals/ must stay out of the zip"
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="*", type=Path)
    ap.add_argument("--status", help="comma-separated statuses to include, e.g. tested,reviewed")
    ap.add_argument("--out", type=Path, default=ROOT / "dist")
    a = ap.parse_args()
    folders = a.folders or sorted(p for p in SKILLS.iterdir() if p.is_dir())
    wanted = set(a.status.split(",")) if a.status else None
    made = 0
    for f in folders:
        f = f.resolve()
        rep = check_skill(f)
        if not rep.ok:
            print(f"[skip] {f.name}: fails tools/check_skill.py")
            continue
        st = skill_status(f)
        if wanted and st not in wanted:
            continue
        z = package(f, a.out)
        print(f"[zip ] {z.relative_to(ROOT) if z.is_relative_to(ROOT) else z}  ({st})")
        made += 1
    print(f"\n{made} zip(s) written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
