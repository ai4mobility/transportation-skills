---
name: journal-club-paper-review
description: Review a transportation research paper (or compare several) and prepare a journal-club presentation with the six-part guide - research problem and scope, contributions, data and methods, key results, language and organization, final evaluation and outlook. Use whenever someone is preparing to present, critique, or compare journal papers for journal club or a reading group, e.g. "help me prepare my journal club on this TR Part C paper", "what are the strengths and limitations of this paper", "compare these two papers on ADAS safety", "make slides for my paper presentation next week", even if they never say "journal club". Produces review notes that point every claim to a page, figure or table, plus a slide outline, and leaves the opinion questions for the presenter to decide. Not for grant proposals or for a referee report to an editor.
license: MIT
metadata:
  version: "1.0.0"
  status: "draft"
  domain: "research-methods"
  authors: "HaoZhouGT"
  sources-checked: "2026-11-15"
  course: "CGN 6933 AI for Mobility, USF, Fall 2026 (worked example 2)"
---

# Journal club: review a transportation paper and plan the talk

A presenter, usually a graduate student, has one or more transportation papers to present
at a weekly journal club. They need review notes that answer the six parts of the
instructor's guide, and a slide outline. This skill does the careful reading and finds the
evidence. The opinion questions stay with the presenter: journal club exists to train their
own critical reading, and they will have to defend those opinions in the room.

## Files

- `references/guide.md`: the instructor's six parts, question by question, each followed by
  "How to answer well" notes. Read it part by part as you fill in the notes.
- `references/transportation_checks.md`: questions to ask of the data, simulation, safety
  measures and models. Not in the guide.
- `references/group_context.md`: the group's research areas, for "connections to our
  group's research". Each group edits it.
- `assets/review_notes.md`: the exact format of the review notes.
- `assets/slide_outline.md`: the format of the slide outline.
- `scripts/rules.py`: the guide's numbers (2-3 strengths, 2-3 limitations), the three
  verdicts, and the slide budget for a slot length.
- `scripts/check_notes.py`: checks the review notes before you hand them over.

## Where each kind of knowledge goes

| Kind | Example from the guide | What the agent does |
|---|---|---|
| Rule (a number) | "2-3 strengths", "2-3 limitations" | `scripts/rules.py` holds them and `scripts/check_notes.py` checks them. Get the slide count from `python3 scripts/rules.py slides <minutes>`. |
| Procedure | The six parts, in order | Follow the steps below. |
| Guidance | "How are those new methods tested and validated?" | Read that part of `references/guide.md`; answer with evidence locations. |
| Judgment (the guide gives it to the presenter) | "How important is the problem in your opinion?" | Give the evidence and a "Draft view", tag it [Presenter's call], and list it under "Questions for the presenter". |
| Experience (not in the guide) | "Are the surrogate safety thresholds justified?" | Use `references/transportation_checks.md` as prompts where they apply. Never present them as the guide's requirements. |

## Steps

1. Get the full text. If you only have the abstract, say so and stop: a review built from
   the abstract repeats the authors' own claims. Ask for the slot length if it is not given.
2. Read the whole paper first, including figures, tables and appendices. Write down page,
   section, figure and table numbers as you go.
3. Fill in `assets/review_notes.md` part by part, with the questions in
   `references/guide.md`. In every part, keep "Paper says" (with its location) apart from
   "Assessment".
4. Build the contribution table: each claimed contribution in the paper's words, the
   evidence for it, and one verdict from `scripts/rules.py`. Check each claim against the
   results, not against the abstract.
5. Check novelty against real prior work if you can search. Cite only papers you found and
   opened, with a DOI or link. Otherwise write "novelty not checked". Never make up a
   reference.
6. Go through `references/transportation_checks.md` and add the checks that apply to this
   paper to parts 3, 4 and 6.
7. For each [Presenter's call], give the evidence and a "Draft view". List all of them under
   "Questions for the presenter".
8. For connections to the group's research, use the projects the presenter names; otherwise
   `references/group_context.md`. If neither fits, ask.
9. Run `python3 scripts/check_notes.py <notes.md>` (add `--papers 2` for two papers) and fix
   every FAIL line.
10. Run `python3 scripts/rules.py slides <minutes>` and write the outline in the format of
    `assets/slide_outline.md`.

## Output

The review notes, passing `scripts/check_notes.py`, and the slide outline. Build the slide
deck itself only if asked, with a source line under every figure taken from the paper.

## Sources

- [S1] Prof. Hao Zhou, "What to cover in your presentation", the guide he gives the
  students in his weekly journal club, Nov 2026. In `references/guide.md`, question by
  question. Typos fixed; one question the guide left unfinished (part 5) is completed and
  marked. Reuse: the author's own text, contributed by him under this repository's license.
- [S2] The "How to answer well" notes in `references/guide.md`,
  `references/transportation_checks.md`, `references/group_context.md`, the verdicts and
  slide budget in `scripts/rules.py`, and `scripts/check_notes.py`. Written for this skill
  on Nov 15, 2026 by the skill's authors with Claude, from common review practice; not yet
  checked with other reviewers. Reuse: original work (MIT).

## Limits

- Verdicts and draft views are the agent's reading, for the presenter to check. The
  presenter decides every [Presenter's call].
- Novelty is judged only against prior work actually found. With no search it stays
  "novelty not checked".
- It cannot tell whether a paper was written with AI. It reports writing style only.
- It needs the full text. Numbers read from figures can be wrong: check them in the paper.
- It does not write referee reports to an editor or review grant proposals.
- The transportation checks are prompts, not a complete list.
