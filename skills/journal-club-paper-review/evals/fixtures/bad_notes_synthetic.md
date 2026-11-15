# Journal club review: CACC paper (bad notes with planted mistakes)

<!-- Each planted mistake is labeled (M1)-(M8). evals/test_scripts.py checks that
scripts/check_notes.py catches every one. -->

One-sentence summary: CACC helps.

## 1. Research problem
Paper says: stop-and-go waves are a problem and no one has studied mixed traffic.
<!-- (M1) "Paper says" with no location -->
Assessment: Looks fine.
[Presenter's call] Is the problem valid? Yes, clearly.
<!-- (M2) presenter's call with no draft view -->

## 2. Contributions
| Claimed contribution (paper's words, location) | Evidence (figure, table or test) | Verdict |
|---|---|---|
| "A novel CACC controller" (p. 1) | Sec. 3 | valid |
| "Validation with real-world field data" | Sec. 4 | not shown |
<!-- (M3) verdict "valid" is not allowed; (M4) second claim has no location -->

Novelty check: similar to earlier CACC work by Smith and others.
<!-- (M5) no DOI or link, and not "novelty not checked" -->

## 3. Data and methods
Paper says: SUMO simulation (Sec. 4).

<!-- (M6) part 4 heading is missing -->

## 5. Language and organization
AI-ish phrases (style only): "delves into" (p. 1). The authors clearly used ChatGPT to write the abstract.
<!-- (M7) says the authors used AI -->

## 6. Final evaluation and outlook
Strengths:
- Clear equation (p. 3).
- Relevant bottleneck (p. 2).
- Short paper (p. 6).
- Uses SUMO (Sec. 4).
Limitations:
- Future work should use more data.
- One seed (Sec. 4).
<!-- (M8) four strengths; first limitation has no location -->

## Questions for the presenter
1. Is the problem valid?
