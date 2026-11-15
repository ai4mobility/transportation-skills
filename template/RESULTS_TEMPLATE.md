# Results: TODO skill name, version TODO

Copy this file to `skills/<your-skill-name>/evals/RESULTS.md` when you move the skill to
`tested`. Fill it in from the `answers.md` you graded. Delete these two lines.

- **Date:** TODO
- **Agent and model (exact):** TODO for example Claude Code 2.1.x with claude-sonnet-5-5
- **Runs:** TODO 3 with skill and 3 without skill, per task, a new workspace each run
- **Graded by:** TODO who, against the expectations in `evals.json`
- **Run folder:** TODO `evals/runs/<date-time>/`

## Load tests

| | Loaded | Total |
|---|---|---|
| Should load | TODO | TODO |
| Should not load (a load here is a false trigger) | TODO | TODO |

## Tasks

Right / partly / wrong, out of the runs for each setup.

| Task | With skill | Without skill | What changed |
|---|---|---|---|
| TODO t1 | TODO 3 / 0 / 0 | TODO 0 / 1 / 2 | TODO one sentence |
| TODO t2 | TODO | TODO | TODO |

## What the skill changed

TODO: in a few sentences, with a quote from one answer with the skill and one without.

## Where it still fails

TODO: the failures, grouped, and what you would change next. A skill that does not beat the
baseline is a valid result: say so and say why.

## How stable the answers were

TODO: how often the grade changed across the 3 runs of the same setup.
