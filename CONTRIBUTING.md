# Contributing a skill

Thank you for adding transportation knowledge that AI agents can use and people can check.

## The one rule

**Every rule a skill states has a source, and every skill has tests.**

A skill is a promise to the agent, and the agent cannot check it. If a step in a SKILL.md
has no source, it is a guess. If a threshold is not in tested code, the agent will compute
it in its head and sometimes get it wrong.

## Skill or tool?

| You are writing... | Put it in |
|---|---|
| How to do a job: what to read, in what order, what to compute, what to check, who decides | A skill, here |
| Code that fetches data or drives software: an API wrapper, an MCP server, a SUMO controller | A tools repository, such as [sumo-agent-tools](https://github.com/ai4mobility/sumo-agent-tools) or [WZDx-Tools](https://github.com/ai4mobility/WZDx-Tools) |

A skill may include small scripts for its own rules and checks, and it may tell the agent to
use a tool from another repository. Say which one under `compatibility:` in the frontmatter.

## Add a skill in seven steps

1. **Pick a job.** Look at [SKILLS_WANTED.md](SKILLS_WANTED.md) and the open issues. Open a
   *Skill proposal* issue so two people do not build the same skill.
2. **Fork the repository and copy the template.**
   `cp -r template/new-skill skills/<your-skill-name>`, then set `name:` to the folder name.
3. **Build it** with the eight steps in [docs/WRITING_SKILLS.md](docs/WRITING_SKILLS.md).
   Look at [`skills/d7-signal-sop`](skills/d7-signal-sop) as you go.
4. **Write the evals and tests.** `evals/evals.json` holds requests that should and should
   not load the skill, and tasks with expectations. `evals/test_*.py` tests every script.
5. **Check it.**
   ```
   pip install -r requirements-dev.txt
   python tools/check_skill.py skills/<your-skill-name>
   python -m pytest -q skills/<your-skill-name>/evals
   ```
   Fix every line marked `x`. Lines marked `!` are advice.
6. **Run the evals** (needed to reach `tested`):
   `python tools/run_evals.py skills/<your-skill-name> --client claude --runs 3`, or
   `--client manual` to do the same runs by hand in claude.ai. Grade `answers.md`, then write
   `evals/RESULTS.md` from [template/RESULTS_TEMPLATE.md](template/RESULTS_TEMPLATE.md).
7. **Open one pull request that changes only `skills/<your-skill-name>/`.** The checks run
   again on GitHub. Changes to `tools/`, docs or other skills go in separate pull requests.

## Names

Name the job, not the document: `mutcd-provision-lookup`, `nhtsa-complaint-reader`, not
`mutcd`. Add the agency when the skill is specific to one: `fdot-...`, `hillsborough-...`.
Use lowercase letters, digits and single hyphens, at most 64 characters. The words "claude"
and "anthropic" are not allowed in a name (claude.ai refuses them).

## The frontmatter

Only the fields of the open format, so the skill works in every agent. Everything specific
to this repository goes under `metadata:`, and every value there is text in quotes.

```yaml
---
name: mutcd-provision-lookup
description: Find the MUTCD 11th Edition provisions that apply to a traffic control device or situation and quote them ... Use when someone asks what the MUTCD requires, recommends or allows ...
license: MIT
compatibility: Needs Python 3.10+ for scripts/. No network access.
metadata:
  version: "0.1.0"
  status: "draft"
  domain: "manuals-and-standards"
  authors: "your-github-username, a-teammate"
  sources-checked: "2026-11-20"
---
```

| Field | What to write |
|---|---|
| `description` | What it does and when to use it, in the words people use when they ask. Up to 1,024 characters, no `<` or `>`. This line decides when the skill loads. |
| `version` | `0.1.0` to start. Raise the last number for wording, the middle for new steps or rules, the first for a new edition of the source. |
| `status` | `draft`, `tested` or `reviewed` (see the README). |
| `domain` | One of: `manuals-and-standards`, `safety-data`, `simulation`, `traffic-operations`, `emergency-response`, `data-feeds`, `vehicle-technology`, `planning-and-design`, `research-methods`, `agency-forms`. To add one, send a separate pull request changing `DOMAINS` in `tools/check_skill.py`. |
| `authors` | GitHub usernames, separated by commas. |
| `sources-checked` | The date someone last confirmed the sources are the current editions. |
| `reviewed-by` | Only for `reviewed`: the reviewer's role, organization and date, for example `"Traffic operations engineer, FDOT District 7, 2026-12-01"`. |

## Sources: what you may copy into a skill

Every item under `## Sources` in SKILL.md ends with a `Reuse:` note.

**Never add the source document itself** (a PDF, Word or PowerPoint file), even a public one.
Put only the pieces the job needs into `references/` as text, and say under `## Sources`
where the full document can be found. The checker fails a skill that contains one.

| Kind of source | Examples | What you may put in the skill | Reuse note |
|---|---|---|---|
| U.S. federal government work | MUTCD (FHWA), NHTSA complaint data, FARS manuals | Quote and copy. Works of the U.S. federal government are not under copyright in the U.S. | `Reuse: public domain (U.S. federal work)` |
| State and local agency documents | FDOT manuals, district SOPs, county plans | Usually public records. Check the agency's terms, quote only what the job needs, cite pages. Internal documents only with written permission. | `Reuse: public agency document, quoted` or `Reuse: permission from <role>, <date>` |
| Copyrighted standards, books and papers | Highway Capacity Manual, AASHTO Green Book, ITE handbooks, journal papers | Cite by section and page and write the steps in your own words. Never copy their text, tables or figures. | `Reuse: cited only` |
| Openly licensed material | CC BY reports, open datasets | Follow the license and name it. | `Reuse: open license (CC BY 4.0)` |
| What people told you | Interviews with operators, inspectors, engineers | Their role and the date, never their name, and only with their agreement. | `Reuse: recorded with the speaker's agreement` |

## Data rules

- No personal information: names, plates, addresses, faces, phone numbers.
- No data you received under a use agreement, including course datasets shared on Canvas.
- No API keys or passwords. The checker looks for common key formats, but it is your job.
- Test files should be small and synthetic. Write SYNTHETIC at the top.
- Link to large data instead of copying it. Files over 5 MB fail the checks.

## Moving up the trust levels

- **draft → tested.** Run the evals: every task with and without the skill, 3 runs each, same
  model, a new chat each run. Grade by hand (right, partly, wrong, and why). Write
  `evals/RESULTS.md` and set `status: "tested"`. A skill that does not beat the baseline is
  still a useful result: say so, and say why.
- **tested → reviewed.** A practicing professional who does this job reads the skill and
  `RESULTS.md` and says they agree, in the pull request or in writing to the maintainer. Add
  `reviewed-by:` with their role, organization and date. Use their name only if they ask.

## What reviewers look for

- Does the description match how people really ask, including field words?
- Does every step trace to a source or to a named person?
- Are the numbers in code, with tests that use values checked in the source?
- Does the skill stop and hand the decision to a person where the agency says a person decides?
- Do the expectations in `evals.json` follow from the source, not from the model's answers?
- Is any copyrighted text copied?

## Keeping a skill current

Check the sources at least once a year, and whenever the manual, the SOP or the agency's app
changes. Update `sources-checked`, raise the version, and re-run the evals if any step changed.

## For students in AI for Mobility

The assignment page on Canvas says what is graded. The note in [AGENTS.md](AGENTS.md) tells
your AI coding assistant what it may and may not write for you; leave it in place. Your
GitHub username is public on a pull request. If you would rather not post course work
publicly, ask the instructor for another way to submit.

## License

Everything you write here is released under the repository's [MIT license](LICENSE): anyone
may use, copy, change and share it, including in paid work, as long as they keep the
copyright notice. You keep the copyright to your own work; the license is the permission
you give everyone else. GitHub's terms make this automatic: content added to a repository
that has a license is licensed under the same terms, so there is no extra form to sign.

Text you quote from a source is not yours to license, so the MIT license does not cover it.
It keeps its source's terms, which is why every source needs a `Reuse:` note. If a skill
quotes a source, say so in its `license:` field, as `skills/d7-signal-sop` does.
