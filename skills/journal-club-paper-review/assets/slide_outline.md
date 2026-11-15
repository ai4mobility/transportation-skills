# Slide outline format

Get the slide count for each part from `python3 scripts/rules.py slides <minutes>` (add
`--papers 2` for two papers). Then write one block per slide:

```
Slide [n]. [Title written as a claim]
- [bullet]
- [bullet]
Show: [Fig. n / Table n from the paper, or "pipeline diagram", or nothing]
Speaker note: [what to say, and where the evidence is in the paper]
```

Write each title as a claim, not a topic: "Delay falls 18% at 50% penetration, from one
seed only" rather than "Results". The audience gets the point even if they miss the
bullets. Use two to four bullets per slide.

The parts, in the order `scripts/rules.py` returns them:

| Part | What the slides show |
|---|---|
| title | Paper, authors, venue, year |
| problem | The problem and why it matters (gap and scope too, when there is no separate slide) |
| gap_scope | The gap, and what is in and out of scope |
| contributions | The contribution table with verdicts |
| methods | The data and method pipeline |
| results | The paper's own figures or tables, labeled with their numbers |
| comparison | The comparison table (two or more papers only) |
| language | Language and organization |
| strengths_limitations | 2-3 strengths and 2-3 limitations |
| takeaways | Takeaways and connections to the group's research |
| discussion | Two or three open questions for the group |

Under every figure or table taken from the paper, add a source line, such as
"Fig. 5 in Smith et al., 2025".
