# Review notes format

Copy this structure. Keep the `##` headings, the "Paper says:" and "Novelty check:" labels,
the contribution table, and the "Strengths:" / "Limitations:" lists exactly as written:
`scripts/check_notes.py` looks for them. Words in [square brackets] are yours to replace.

A location is a page, section, figure, table, equation or appendix: `p. 4`, `Sec. 3.2`,
`Fig. 5`, `Table 2`, `Eq. 7`, `Appendix B`.

```
# Journal club review: [short title] ([first author] et al., [year], [journal])

Presenter: [name] | Date: [date] | Slot: [minutes] min
One-sentence summary: [the problem and the main finding, in plain words]

## 1. Research problem
Paper says: [the problem and the gap, in the paper's terms] (p. [n])
Assessment: [Is the gap established by the paper's own literature review? Is the scope big
enough to matter and small enough to handle? What is left out?]
[Presenter's call] Is the problem valid? Draft view: [...]
[Presenter's call] How important is it for transportation goals? Draft view: [...]

## 2. Contributions
| Claimed contribution (paper's words, location) | Evidence (figure, table or test) | Verdict |
|---|---|---|
| "[claim]" (p. [n]) | [Table n / Fig. n / the test] | [supported / partly supported / not shown] |

Novelty check: [closest prior work found, with DOI or link] or "novelty not checked"

## 3. Data and methods
Paper says: [data and method] (Sec. [n])
Pipeline: data -> processing -> model -> output -> validation
Key assumptions, and what breaks if each fails: [...]
Assessment: [Are the data and methods appropriate for the research question?]

## 4. Key results
Paper says: [main findings] (Table [n], Fig. [n])
Figures and tables to show: [...]
Assessment: [Are the conclusions supported? Do abstract, text and tables match? Is
variation reported?]

## 5. Language and organization
Well written: [passage, location, why]
Ambiguous: [passage, location, why]
AI-ish phrases (style only): ["short phrase" (p. n), ...]
Structure: [...]
[Presenter's call] What would you borrow or avoid in your own writing? Draft view: [...]

## 6. Final evaluation and outlook
Strengths:
- [one sentence] ([location])
- [one sentence] ([location])
Limitations:
- [what it could change, and what test would settle it] ([location])
- [...] ([location])
[Presenter's call] Main takeaway for future research. Draft view: [...]
[Presenter's call] Connections to our group's research. Draft view: [...]

## Questions for the presenter
1. [one question per Presenter's call above]

## Comparison
(Only with more than one paper.)
| | Paper A | Paper B |
|---|---|---|
| Research question | | |
| Data | | |
| Method | | |
| Scope | | |
| Key finding | | |
| Implications | | |

The conclusions are [complementary / overlapping / conflicting], because [...].
```
