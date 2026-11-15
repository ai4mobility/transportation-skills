---
name: new-skill
description: TODO what this skill does, for whom, from what input (a manual section, a photo, a narrative, a feed, a simulation output). Then "Use when ..." with the situations, in the words people use when they ask, including field words the manual does not use. Up to 1,024 characters, no angle brackets.
license: MIT
metadata:
  version: "0.1.0"
  status: "draft"
  domain: "TODO one domain from CONTRIBUTING.md"
  authors: "TODO your-github-username"
  sources-checked: "TODO the date you checked the sources, like 2026-11-20"
---

# TODO: the job this skill does, in one line

TODO: one short paragraph. Who asks, what they need back, and in what form. What this skill
covers and what it does not.

## Files

- `references/knowledge.md`: the pieces of the source the job needs, each with an id and
  the source's exact words (or your own words, for a source you may only cite).
- `references/glossary.md`: field words mapped to the source's words.
- `references/lessons.md`: lessons from past events and other documents. Not the source.
- `references/practice.md`: what experienced people told you. Not the source.
- `scripts/rules.py`: the source's numbers, times and thresholds as code.
- `assets/output_format.md`: the exact format of the answer.

Delete any line (and file) the job does not need.

## Where each kind of knowledge goes

| Kind | Example from your source | What the agent does |
|---|---|---|
| Rule (a number, a time, a threshold) | TODO | Run `scripts/rules.py`. Never compute it in its head. |
| Procedure (ordered steps) | TODO | Follow the steps below and cite the piece id. |
| Guidance (long text) | TODO | Read one section of `references/knowledge.md` and quote it. |
| Judgment (the source gives it to a person) | TODO | Write "Person decides: yes" and name who. |
| Experience (not in the source) | TODO | A suggestion that cites L# or P#, never a rule. |

## Steps

1. TODO: translate the request into the source's words with `references/glossary.md`.
2. TODO: find the part of the source that applies, and read only that part.
3. TODO: for every number, time or threshold, run `scripts/rules.py` and copy its result.
4. TODO: write the answer in the format of `assets/output_format.md`, citing piece ids.
5. TODO: mark every decision the source gives to a person: who decides, and why.
6. TODO: add suggestions from `references/lessons.md` and `references/practice.md` where
   they apply, kept apart from the source.
7. TODO: end with what the source does not answer, and who to ask.

## Output

TODO: what the answer contains, and nothing else.

## Sources

- [S1] TODO: title, edition or version, date, the pages or sections used. Reuse: TODO
  (public domain / public agency document, quoted / open license, name it / permission
  from whom and when / cited only).

## Limits

- TODO: what this skill does not cover.
- TODO: what a person decides, and who.
