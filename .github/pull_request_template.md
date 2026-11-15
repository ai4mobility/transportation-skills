<!-- A skill pull request changes one folder, skills/<name>/. Keep every section short. -->

## The job

<!-- Who asks, what they decide with the answer, how often. One or two sentences. -->

## Sources

<!-- The main sources, with edition and pages, and how the skill reuses them (quoted / cited only / permission). -->

## The knowledge it adds

<!-- The two things this skill knows that a general model gets wrong without it, each with its source and the test that holds it. -->

## Evals

<!-- Status (draft / tested / reviewed). If tested: the table from evals/RESULTS.md and one sentence on what changed. -->

## AI use

<!-- What an AI assistant wrote (code, tests, wording) and what you wrote and checked yourself. -->

## Checklist

- [ ] `python tools/check_skill.py skills/<name>` passes on my computer
- [ ] `python -m pytest -q skills/<name>/evals` passes
- [ ] this pull request changes only `skills/<name>/`
- [ ] no personal information, restricted data or API keys
- [ ] no text, tables or figures copied from a source whose reuse note is "cited only"
