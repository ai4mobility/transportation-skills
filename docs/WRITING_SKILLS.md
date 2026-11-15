# Writing a skill: eight steps

A skill is written for a **job**, not for a document. The same SOP can become three skills:
one that looks things up, one that writes action cards, one that checks a plan. Start from
the job.

The worked example for every step is [`skills/d7-signal-sop`](../skills/d7-signal-sop),
built from the FDOT District 7 Traffic Signals SOP v1.5.

A second example, [`skills/journal-club-paper-review`](../skills/journal-club-paper-review),
is built from an instructor's guide for presenting journal papers. The SOP job is mostly
procedure; this one is mostly judgment, so its main design choice is what the agent does
and what the presenter decides (the "[Presenter's call]" items).

| # | Step | What you write down | D7 example |
|---|---|---|---|
| 1 | **Name the job.** Who asks, what they need back, in what form. | One sentence, and three requests in the words people really use. | The signal team the morning after landfall needs action cards that cite the SOP. |
| 2 | **Keep the source's exact words.** Edition or version, date, pages, an id for every piece. | The source list, and the pieces with ids. | 150 clauses from PDF pp. 5-11, with ids like `Post-Storm > Immediately Post Storm > 3.2.1`. |
| 3 | **Sort every piece into a home.** Rule → code. Procedure → steps. Long guidance → retrieve and quote. A decision the source gives to a person → "Person decides". | A table: piece id, kind, home. For a procedure, the weight read from its verbs. | Refuel times → `scripts/rules.py`. Generator priorities → TMC personnel. 18 must, 123 standard, 9 consider. |
| 4 | **Write the reading path.** The steps an experienced person follows: what to read first, what to compute, when to stop and ask. | The numbered steps in SKILL.md. | Find the phase → read that section → run the rules → write cards → flag decisions → read the gaps → check. |
| 5 | **Add what the document leaves out.** Field words, lessons written after real events, practice from people who did the work. Keep each apart from the source, with where it came from. | `references/glossary.md`, `lessons.md`, `practice.md`. | 48 field phrases; 6 lessons from FDOT, Hillsborough and Pinellas documents; practice from an interview. |
| 6 | **Write the description** in the words of the requests from step 1, and say when to use it. | The `description:` line. | "...even in field words ('the lights are dark', 'top off the backup power')". |
| 7 | **Test before you trust it.** Requests that should and should not load it; tasks written before any run; a checker in code; runs with and without the skill. | `evals/evals.json`, `evals/test_*.py`, later `evals/RESULTS.md`. | `scripts/check_cards.py`: 9 of 9 example cards pass; 4 of 4 planted card mistakes and 4 of 4 planted suggestion mistakes caught. |
| 8 | **Keep it current.** Who maintains it, and what triggers a re-check (a new edition, a new season, a changed form). | `version` and `sources-checked` in the frontmatter. | SOP v1.5, June 2025; lessons dated; practice re-checked each season. |

## Step 3 in more detail: four homes

| Kind of knowledge | Example | Home | Why |
|---|---|---|---|
| Rule: a number, a time, a threshold | "First refueling six hours after initial deployment"; MUTCD taper lengths; a warrant's volume threshold | `scripts/`, with a test | Models make arithmetic and date mistakes. Code does not. |
| Procedure: ordered steps | the Immediately Post Storm steps | The steps in SKILL.md, citing the piece id | The agent follows the order an expert follows. |
| Guidance: long text read as needed | a manual chapter, an after-action report | `references/`, read one section at a time and quoted | Loading the whole manual wastes context and buries the part that matters. |
| Judgment: a decision the source gives to a person | "TMC personnel to determine generator deployment priorities"; "engineering judgment" | "Person decides: yes", and who | The agent drafts. The person named in the source decides. |

Gaps go in a list (`references/gaps.md` in the D7 skill). Never fill a gap from memory.

## Step 5 in more detail: experience

- Experience never becomes a rule by itself. It is a **suggestion** that cites its id (L1,
  P2) and leaves the decision to a person, or a hard case in `references/edge_cases.md`
  that an expert has read and agreed to.
- Write down who said it (role, not name) and when. Practice changes faster than manuals.
- When experience and the source disagree, keep both and flag the conflict. Do not pick a winner.
- Lessons come from documents written after real events: after-action reports, agency
  presentations, case studies, news reports quoting agency documents. Cite each one.
- Practice comes from people. [INTERVIEW_THE_EXPERT.md](INTERVIEW_THE_EXPERT.md) has ten
  questions for a 20-minute interview.

## Writing the description

The agent sees only the descriptions of all its skills when it decides which one to open.
So the description is the most important line in the skill.

- Say what the skill does, then "Use when ..." with the situations, in people's words.
- Include the words people use that the manual does not ("the lights are dark").
- Name what it is not for, if a near neighbor could be confused with it.
- Up to 1,024 characters, and no `<` or `>`.

## Writing the evals

`evals/evals.json` has three parts. Write them **before** you run the skill, so the runs
cannot shape them.

- `should_load`: at least 3 requests that should open the skill. Use field words. Include at
  least one that never names the manual.
- `should_not_load`: at least 3 near misses: the same topic, a different job. For the D7
  skill: a yellow-interval question (signals, but not the hurricane SOP), a debris question
  (hurricanes, but not signals).
- `tasks`: at least 2. Each has an `id`, a `prompt`, optional `files` (in `evals/files/`,
  marked SYNTHETIC), and `expectations`: checkable statements a right answer meets, each
  traceable to the source or to the output of your own script.

Then run them with and without the skill (`tools/run_evals.py`). The rules for a fair
comparison:

1. Same prompt, same model, a new chat or workspace for every run, 3 runs each.
2. Do not edit the skill while you are scoring. If you fix something, run all of it again.
3. Grade by hand against the expectations: right, partly or wrong, and why.
4. Write down exactly which model you used.
5. Report how often answers changed between runs.
6. The skill losing is a valid result. Report it and say what you think went wrong.
7. Make sure no other copy of the skill is installed (a Claude Code plugin, a claude.ai
   upload), or the "without" runs are not without it. `run_evals.py` flags a "without" run
   that opened the skill, when it can see it.

`evals/` is never shown to the model: `run_evals.py` and `package_skills.py` both leave it out.

## Common mistakes

| Mistake | What happens | Fix |
|---|---|---|
| The description names the manual but not the job | The skill loads for every question about the manual, or never | Start the description with the job and the situations |
| Thresholds written in prose | The agent does the arithmetic itself and is sometimes wrong | Move them to `scripts/`, with a test |
| The whole manual pasted into SKILL.md | Slow, expensive, and the key section gets lost | Keep SKILL.md under 500 lines; put sections in `references/` |
| Lessons written as rules | Experience is presented as if the agency required it | Keep lessons separate and output them as suggestions |
| Expected answers copied from a model's output | The test measures the model against itself | Take expected answers from the source or your own checked calculation |
| Copyrighted tables copied in | The skill cannot be shared | Cite the table by number and page; put the numbers you need in code only if their reuse allows it |
