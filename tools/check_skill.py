"""Check a skill folder before it goes into the repository.

Two kinds of checks:

  A. The open Agent Skills format (agentskills.io/specification), so the skill loads in
     Claude, Codex, Copilot, Gemini CLI, Cursor and any other client that follows it:
     the SKILL.md frontmatter, the name rules, the description length, the body length.

  B. This repository's rules, so a reader can trust what the skill says:
     sources with a reuse note, limits and who decides, metadata (status, domain,
     authors, version, date the sources were checked), evals, tests for any script,
     files the SKILL.md mentions actually exist, no secrets, no huge files.

Run (from the repository root):
  python tools/check_skill.py skills/<name>          one skill
  python tools/check_skill.py --all                  every folder in skills/
  python tools/check_skill.py --changed <base-sha>   the skills a pull request touches
                                                     (also checks the pull request's scope)
Exit code 1 if anything fails. Warnings never fail.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

# --- A. the open format -------------------------------------------------------------
SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
RESERVED_WORDS = ("claude", "anthropic")      # claude.ai refuses skill names with these
MAX_BODY_LINES = 500

# --- B. this repository -------------------------------------------------------------
STATUSES = ("draft", "tested", "reviewed")
DOMAINS = (
    "manuals-and-standards",   # MUTCD, design manuals, SOPs, specifications
    "safety-data",             # crash reports, NHTSA complaints, FARS, narratives
    "simulation",              # SUMO, cellular automata, digital twins
    "traffic-operations",      # signals, TSM&O, work zones, incident management
    "emergency-response",      # hurricanes, evacuation, post-storm work
    "data-feeds",              # WZDx, GTFS, 511, probe and sensor data
    "vehicle-technology",      # ADAS, automated driving, EVs, vehicle data
    "planning-and-design",     # planning studies, geometric design, capacity
    "research-methods",        # reading papers, experiment design, evaluation
    "agency-forms",            # filling an agency's app or form (Survey123, crash forms)
)
REQUIRED_METADATA = ("version", "status", "domain", "authors", "sources-checked")
MIN_SHOULD_LOAD, MIN_SHOULD_NOT_LOAD, MIN_TASKS = 3, 3, 2
MAX_FILE_MB, MAX_SKILL_MB = 5, 20
STALE_DAYS = 365

FILE_REF_RE = re.compile(r"(?<![\w/.-])((?:references|scripts|assets)/[A-Za-z0-9_./-]*[A-Za-z0-9_])")
SECRET_PATTERNS = [
    (re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "an Anthropic API key"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{32,}"), "an API key (sk-...)"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "an AWS access key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{30,}"), "a GitHub token"),
    (re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}"), "a GitHub token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}"), "a Slack token"),
    (re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"), "a private key"),
]
FORBIDDEN_NAMES = re.compile(r"^(\.env.*|.*\.pem|.*\.key|credentials.*|.*secrets?\..*)$", re.I)
JUNK_NAMES = re.compile(r"^(\.DS_Store|Thumbs\.db|__pycache__|.*\.pyc)$")
# The source document itself never goes into a skill, even a public one: only the pieces
# the job needs, as text in references/, with a link to where the document can be found.
SOURCE_DOC_SUFFIXES = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".key", ".pages"}


class Report:
    def __init__(self, folder: Path):
        self.folder = folder
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors

    def print(self) -> None:
        mark = "PASS" if self.ok else "FAIL"
        try:
            shown = self.folder.relative_to(ROOT)
        except ValueError:
            shown = self.folder
        print(f"[{mark}] {shown}")
        for e in self.errors:
            print(f"       x {e}")
        for w in self.warnings:
            print(f"       ! {w}")


def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """Return (frontmatter, body, problem)."""
    if not text.startswith("---"):
        return None, text, "SKILL.md must start with a '---' line (YAML frontmatter)"
    parts = text.split("\n")
    try:
        end = next(i for i in range(1, len(parts)) if parts[i].strip() == "---")
    except StopIteration:
        return None, text, "the frontmatter has no closing '---' line"
    raw = "\n".join(parts[1:end])
    try:
        fm = yaml.safe_load(raw) or {}
    except yaml.YAMLError as e:
        return None, text, f"the frontmatter is not valid YAML: {e}".split("\n")[0]
    if not isinstance(fm, dict):
        return None, text, "the frontmatter must be a set of 'key: value' lines"
    return fm, "\n".join(parts[end + 1:]), None


def section(body: str, title_start: str) -> str | None:
    """Text of the first '## <title_start>...' section, or None."""
    m = re.search(rf"(?mi)^##[ \t]+{re.escape(title_start)}.*$", body)
    if not m:
        return None
    rest = body[m.end():]
    nxt = re.search(r"(?m)^##[ \t]+\S", rest)
    return rest[: nxt.start()] if nxt else rest


def list_items(text: str) -> list[str]:
    """Top-level '- item' entries, each joined with its indented continuation lines."""
    items: list[str] = []
    for line in text.split("\n"):
        m = re.match(r"^[-*][ \t]+(.+)$", line)
        if m:
            items.append(m.group(1).strip())
        elif items and line.startswith((" ", "\t")) and line.strip():
            items[-1] += " " + line.strip()
    return items


def check_frontmatter(fm: dict, folder: Path, r: Report) -> None:
    extra = sorted(set(fm) - SPEC_FIELDS)
    if extra:
        r.err(f"frontmatter field(s) {', '.join(extra)} are not in the open format; "
              "put them under 'metadata:' or remove them")

    name = fm.get("name")
    if not isinstance(name, str) or not name:
        r.err("frontmatter needs 'name'")
    else:
        if len(name) > 64:
            r.err(f"name is {len(name)} characters; the limit is 64")
        if not NAME_RE.match(name):
            r.err(f"name '{name}' may use only lowercase letters, digits and single hyphens, "
                  "and cannot start or end with a hyphen")
        if name != folder.name:
            r.err(f"name '{name}' must match the folder name '{folder.name}'")
        for word in RESERVED_WORDS:
            if word in name:
                r.err(f"name contains '{word}', which claude.ai does not accept in a skill name")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        r.err("frontmatter needs a 'description' (what the skill does and when to use it)")
    else:
        if len(desc) > 1024:
            r.err(f"description is {len(desc)} characters; the limit is 1,024")
        if "<" in desc or ">" in desc:
            r.err("description cannot contain '<' or '>' (claude.ai refuses the upload)")
        if len(desc) < 80:
            r.warn(f"description is only {len(desc)} characters; say what it does AND when to "
                   "use it, in the words people use when they ask")
        if not re.search(r"(?i)\buse (it )?(when|for|whenever)\b", desc):
            r.warn("description does not say when to use the skill ('Use when ...')")

    comp = fm.get("compatibility")
    if comp is not None and (not isinstance(comp, str) or not 1 <= len(comp) <= 500):
        r.err("compatibility must be text of 1 to 500 characters")

    tools = fm.get("allowed-tools")
    if tools is not None and not isinstance(tools, str):
        r.err("allowed-tools must be one space-separated string")

    md = fm.get("metadata")
    if not isinstance(md, dict):
        r.err("frontmatter needs 'metadata:' with " + ", ".join(REQUIRED_METADATA))
        return
    for k, v in md.items():
        if not isinstance(k, str) or not isinstance(v, str):
            r.err(f"metadata '{k}' must be text; put quotes around it, e.g. {k}: \"{v}\"")
    for k in REQUIRED_METADATA:
        if not md.get(k):
            r.err(f"metadata needs '{k}'")

    status = md.get("status")
    if isinstance(status, str) and status and status not in STATUSES:
        r.err(f"metadata status must be one of {', '.join(STATUSES)}, not '{status}'")
    domain = md.get("domain")
    if isinstance(domain, str) and domain and domain not in DOMAINS:
        r.err(f"metadata domain '{domain}' is not in the list in tools/check_skill.py "
              "(DOMAINS); pick one, or propose a new one in a separate pull request")
    version = md.get("version")
    if isinstance(version, str) and version and not re.match(r"^\d+\.\d+\.\d+$", version):
        r.err(f"metadata version must look like 1.0.0, not '{version}'")
    checked = md.get("sources-checked")
    if isinstance(checked, str) and checked:
        try:
            d = date.fromisoformat(checked)
            age = (date.today() - d).days
            if age > STALE_DAYS:
                r.warn(f"sources were last checked {age} days ago ({checked}); check that the "
                       "manuals and documents are still the current versions")
            if age < 0:
                r.err(f"sources-checked {checked} is in the future")
        except ValueError:
            r.err(f"metadata sources-checked must be a date like 2026-11-15, not '{checked}'")
    if status == "reviewed" and not md.get("reviewed-by"):
        r.err("status 'reviewed' needs metadata 'reviewed-by': the reviewer's role, "
              "organization and date (for example: \"Signal engineer, FDOT D7, 2026-12-01\")")


def check_body(body: str, folder: Path, r: Report) -> None:
    lines = body.strip("\n").split("\n")
    if len(lines) > MAX_BODY_LINES:
        r.err(f"SKILL.md body is {len(lines)} lines; keep it under {MAX_BODY_LINES} and move "
              "detail into references/")
    if len(body.strip()) < 200:
        r.err("SKILL.md body is nearly empty; write the steps an experienced person follows")

    src = section(body, "Sources")
    if src is None:
        r.err("SKILL.md needs a '## Sources' section: every manual, dataset or document the "
              "skill relies on, with version and pages")
    else:
        items = list_items(src)
        if not items:
            r.err("'## Sources' has no list items ('- [S1] ...')")
        for it in items:
            if "reuse:" not in it.lower():
                r.err(f"source has no 'Reuse:' note (public domain / open license / permission / "
                      f"cited only): {it[:70]}")

    lim = section(body, "Limits")
    if lim is None:
        r.err("SKILL.md needs a '## Limits' section: what the skill does not cover and what a "
              "person decides")
    elif not list_items(lim):
        r.err("'## Limits' has no list items")

    seen = set()
    for ref in FILE_REF_RE.findall(body):
        ref = ref.rstrip(".")
        if ref in seen:
            continue
        seen.add(ref)
        if not (folder / ref).exists():
            r.err(f"SKILL.md mentions {ref}, which does not exist in the skill folder")
        elif ref.count("/") > 1:
            r.warn(f"{ref} is more than one folder deep; keep references one level from SKILL.md")


def check_todos(path: Path, r: Report) -> None:
    hits = [i for i, line in enumerate(path.read_text(errors="ignore").split("\n"), 1) if "TODO" in line]
    if hits:
        where = f"line {hits[0]}" if len(hits) == 1 else f"{len(hits)} lines, first at line {hits[0]}"
        r.err(f"{path.relative_to(r.folder)} still has TODO ({where}); fill it in or delete it")


def check_evals(folder: Path, status: str | None, r: Report) -> None:
    ev = folder / "evals" / "evals.json"
    if not ev.exists():
        r.err("missing evals/evals.json (requests that should and should not load the skill, "
              "and tasks with expectations)")
        return
    try:
        data = json.loads(ev.read_text())
    except json.JSONDecodeError as e:
        r.err(f"evals/evals.json is not valid JSON: {e}")
        return
    check_todos(ev, r)
    if data.get("skill") != folder.name:
        r.err(f"evals/evals.json 'skill' must be '{folder.name}'")
    for key, n in (("should_load", MIN_SHOULD_LOAD), ("should_not_load", MIN_SHOULD_NOT_LOAD)):
        items = data.get(key)
        if not isinstance(items, list) or len([x for x in items if isinstance(x, str) and x.strip()]) < n:
            r.err(f"evals/evals.json needs at least {n} '{key}' requests, written the way "
                  "people really ask")
    tasks = data.get("tasks")
    if not isinstance(tasks, list) or len(tasks) < MIN_TASKS:
        r.err(f"evals/evals.json needs at least {MIN_TASKS} tasks")
        tasks = tasks if isinstance(tasks, list) else []
    ids = set()
    for t in tasks:
        if not isinstance(t, dict):
            r.err("each task in evals/evals.json must be an object")
            continue
        tid = t.get("id")
        if not tid or tid in ids:
            r.err(f"every task needs a unique 'id' (got {tid!r})")
        ids.add(tid)
        if not str(t.get("prompt", "")).strip():
            r.err(f"task {tid}: needs a 'prompt'")
        exp = t.get("expectations")
        if not isinstance(exp, list) or not exp:
            r.err(f"task {tid}: needs 'expectations', the checkable things a right answer does")
        for f in t.get("files", []) or []:
            if not (folder / "evals" / f).exists():
                r.err(f"task {tid}: file evals/{f} does not exist")

    results = folder / "evals" / "RESULTS.md"
    if status in ("tested", "reviewed"):
        if not results.exists():
            r.err(f"status '{status}' needs evals/RESULTS.md: runs with and without the skill")
        else:
            t = results.read_text(errors="ignore").lower()
            if "with skill" not in t or "without skill" not in t or "|" not in t:
                r.err("evals/RESULTS.md needs a table comparing 'with skill' and 'without skill'")
    if results.exists():
        check_todos(results, r)


def check_files(folder: Path, r: Report) -> None:
    total = 0
    scripts = [p for p in (folder / "scripts").rglob("*.py")] if (folder / "scripts").is_dir() else []
    tests = list((folder / "evals").glob("test_*.py")) if (folder / "evals").is_dir() else []
    if scripts and not tests:
        r.err("scripts/ has Python code but evals/ has no test_*.py: every rule in code needs a test")
    for p in sorted(folder.rglob("*")):
        rel = p.relative_to(folder)
        if any(JUNK_NAMES.match(part) for part in rel.parts):
            continue      # caches and OS files: .gitignore keeps them out, the zip leaves them out
        if p.is_dir():
            continue
        if FORBIDDEN_NAMES.match(p.name):
            r.err(f"{rel} looks like a secrets file; never commit keys or passwords")
        if p.suffix.lower() in SOURCE_DOC_SUFFIXES:
            r.err(f"{rel} is a document file. A skill holds the pieces of a source it needs as text "
                  "in references/, not the document itself; say in '## Sources' where to find it")
        size = p.stat().st_size
        total += size
        if size > MAX_FILE_MB * 1024 * 1024:
            r.err(f"{rel} is {size / 1e6:.1f} MB; the limit is {MAX_FILE_MB} MB per file. Link to "
                  "large data instead of copying it")
        if size < 2_000_000:
            try:
                text = p.read_text(errors="ignore")
            except OSError:
                continue
            for pat, what in SECRET_PATTERNS:
                if pat.search(text):
                    r.err(f"{rel} seems to contain {what}; remove it and revoke the key")
    if total > MAX_SKILL_MB * 1024 * 1024:
        r.err(f"the skill folder is {total / 1e6:.1f} MB; the limit is {MAX_SKILL_MB} MB")


def check_skill(folder: Path) -> Report:
    folder = folder.resolve()
    r = Report(folder)
    skill_md = folder / "SKILL.md"
    if not skill_md.exists():
        r.err("missing SKILL.md")
        return r
    fm, body, problem = split_frontmatter(skill_md.read_text())
    if problem:
        r.err(problem)
        return r
    check_frontmatter(fm, folder, r)
    check_body(body, folder, r)
    check_todos(skill_md, r)
    for sub in ("references", "assets"):
        if (folder / sub).is_dir():
            for f in sorted((folder / sub).rglob("*")):
                if f.is_file() and f.suffix.lower() in (".md", ".txt", ".json", ".csv", ".yaml", ".yml"):
                    check_todos(f, r)
    status = (fm.get("metadata") or {}).get("status") if isinstance(fm.get("metadata"), dict) else None
    check_evals(folder, status, r)
    check_files(folder, r)
    return r


def pr_scope_problems(paths: list[str]) -> list[str]:
    """A pull request that changes a skill changes only that one folder, skills/<name>/."""
    skill_dirs = {p.split("/")[1] for p in paths if p.startswith("skills/") and p.count("/") >= 2}
    others = [p for p in paths if not p.startswith("skills/")]
    problems = []
    if len(skill_dirs) > 1:
        problems.append("this pull request changes more than one skill (" + ", ".join(sorted(skill_dirs))
                        + "); send one pull request per skill")
    if skill_dirs and others:
        problems.append("a skill pull request changes only skills/<name>/; send changes to "
                        + ", ".join(sorted(others)[:5]) + " in a separate pull request")
    return problems


def changed_paths(base: str) -> list[str]:
    out = subprocess.run(["git", "diff", "--name-only", base, "HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\n") if p.strip()]


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    folders: list[Path] = []
    scope: list[str] = []
    if argv[0] == "--all":
        folders = sorted(p for p in SKILLS.iterdir() if p.is_dir()) if SKILLS.is_dir() else []
    elif argv[0] == "--changed":
        paths = changed_paths(argv[1])
        scope = pr_scope_problems(paths)
        names = sorted({p.split("/")[1] for p in paths if p.startswith("skills/") and p.count("/") >= 2})
        for n in names:
            if (SKILLS / n).is_dir():
                folders.append(SKILLS / n)
            else:
                print(f"[note] skills/{n} was removed in this pull request")
        if not names:
            print("[note] this pull request changes no skill folder; only the scope rule applies")
    else:
        folders = [Path(a) for a in argv]
    ok = True
    for s in scope:
        print(f"[FAIL] pull request scope\n       x {s}")
        ok = False
    reports = [check_skill(f) for f in folders]
    for rep in reports:
        rep.print()
        ok = ok and rep.ok
    if reports:
        print(f"\n{sum(r.ok for r in reports)} of {len(reports)} skill(s) pass.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
