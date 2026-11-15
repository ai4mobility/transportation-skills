---
name: d7-signal-sop
description: Turn the FDOT District 7 Traffic Signals SOP (v1.5, June 2025) into action cards for hurricane response - pre-storm preparation, post-storm signal status from ATMS, generator deployment and refueling, SAT and DAT passes, eSTORM updates, emergency TWOs and DDIR funding. Use when someone asks what the signal team should do next before or after a storm in District 7, or asks whether a plan follows the SOP, even in field words ("the lights are dark", "top off the backup power"). Every action cites an SOP clause word for word; lessons from past storms come separately, as suggestions.
license: MIT for this skill's own text and code; the quoted SOP clauses remain FDOT's (see Sources)
metadata:
  version: "1.0.0"
  status: "draft"
  domain: "emergency-response"
  authors: "HaoZhouGT"
  sources-checked: "2026-11-13"
  course: "CGN 6933 AI for Mobility, USF, Fall 2026 (worked example)"
---

# D7 traffic signal SOP: from procedure to action cards

Course demo skill for AI for Mobility (CGN 6933, USF). It is not an FDOT product.
It covers the SOP's pre-storm, post-storm, emergency TWO and funding pages
(PDF pages 5-11). Damage assessment pages and Appendix A are not included.

## Files

- `references/sop_text.md`: every clause with its id, weight and page. Read the
  section for the phase you are in, not the whole file.
- `references/clauses.json`: the same clauses in machine-readable form.
- `references/gaps.md`: what the SOP does not say. Read it before you answer.
- `references/glossary.md`: field words mapped to the SOP's words.
- `references/lessons.md`: lessons from past storms and other FDOT documents. Not the SOP.
- `references/practice.md`: what experienced staff told us. Not the SOP.
- `scripts/rules.py`: the SOP's time and money rules as code.
- `scripts/check_cards.py`: checks your cards and suggestions before you answer.
- `assets/action_card.md`: the card and suggestion format. Fill it in exactly.

## Where each kind of knowledge goes

| Kind | Example in this SOP | What you do |
|---|---|---|
| Rule (a number, a time, a threshold) | first refuel six hours after deployment; encumber within 24 hours; $5,000 DDIR threshold; 1/4-mile grouping | Run `scripts/rules.py`. Never compute these yourself. |
| Procedure (ordered steps) | the Immediately Post Storm steps | Follow `references/sop_text.md` and cite the clause. |
| Guidance (long documents) | an after-action report, the MUTCD, a county plan | Use only if the user provides it. Cite the page. Never fill a gap from memory. |
| Judgment (the SOP gives the decision to a person) | generator priorities (TMC personnel, Three Hours Prior 2.2); crew numbers (operations centers, 24 Hours Prior 1); DDIR grouping (DDIR team, TWO 4) | Write the card, set "Person decides: yes" and name who. |
| Experience (not in the SOP) | stop control when no generator can run a signal (L1); retiming detour routes (L2); what staff told us (P1, P2, ...) | Write a **Suggestion**, never a card. Cite L# or P#. Person decides: yes. |

## Steps

1. Translate the request. Map field words to the SOP's words with
   `references/glossary.md` ("backup power" means generator, "dark" means
   non-operational). Search the SOP in its own words.
2. Find the phase. Pre-storm: hours before landfall. Post-storm: Immediately Post
   Storm, Ongoing Efforts, or 0-1 Week. Money: Emergency TWOs, 0-1 Month, 0-4 Months.
   If the user gives no time line, ask for it before writing cards.
3. Open `references/sop_text.md` and read that phase's clauses.
4. For any time, deadline or dollar rule, run `scripts/rules.py` and copy its
   result into the card's **When** field:
   - `python3 scripts/rules.py atms yellow`
   - `python3 scripts/rules.py refuel "2026-10-10 06:10"`
   - `python3 scripts/rules.py sat "<start>" "<end>"`
   - `python3 scripts/rules.py notice "<notified>" "<deploy>"`
   - `python3 scripts/rules.py encumber "<TWO issued>"`
   - `python3 scripts/rules.py two <issue date> <EO expiry> --soe yes --funding yes`
   - `python3 scripts/rules.py ddir repairs.csv`
5. Write one card per action with `assets/action_card.md`.
   - Quote the SOP words exactly, between straight double quotes.
   - Copy the weight from `sop_text.md`. Never raise a "consider" step to "must".
   - **Who** is the role the SOP names. If it names none, write
     "not stated (Appendix C is blank)".
6. Set **Person decides: yes** when the SOP hands the decision to someone, or when
   the action could put people at risk if it is wrong (energizing a damaged
   signal, sending a crew into a flooded area).
7. Read `references/gaps.md`. When an action needs a zone map, a priority list or
   a responsibility assignment, say it is blank in v1.5 and name who to ask.
   Never invent zone names, priority intersections, phone numbers, pay items or
   costs.
8. Read `references/lessons.md` and `references/practice.md`. Where a lesson or a
   practice entry applies to the situation, add a **Suggestion** after the cards.
   - Cite its id (L1, P2). Never put a lesson in a card's SOP field.
   - Person decides: yes, always, with the role the entry names.
   - If it conflicts with an SOP step, say so in the suggestion. The SOP card stands.
   - If a question is contested (L3, signal head removal), give both sides and do not recommend.
9. End with a short **Not covered** list: what the user asked that neither the SOP
   nor the lessons answer.
10. Check before you answer. Save the cards to a file and run
    `python3 scripts/check_cards.py cards.md`. Fix every FAIL line, then run it again.

## Output

Only the cards, the suggestions and the Not covered list, in the format of
`assets/action_card.md`. `scripts/check_cards.py` reads that format, so do not change
the field names.

## Sources

- [S1] FDOT District 7 Traffic Signals SOP, v1.5, June 2025, PDF pages 5-11, as clauses in
  `references/sop_text.md` and `references/clauses.json`. Reuse: public agency document;
  only the clauses the job needs are quoted, word for word. The PDF itself is not included.
- [S2] Lessons L1-L6 in `references/lessons.md`: FDOT Central Office TEOO slides, a
  Hillsborough County news release, St. Pete Catalyst, and a NOCoE case study; each is
  cited in the file. Reuse: paraphrased and cited, not copied.
- [S3] `references/glossary.md`: written for the course on Nov 14, 2026 from the SOP's own
  words, not with D7 staff. Reuse: original course work (MIT).
- [S4] `references/practice.md`: entries from interviews, each with the speaker's role and
  date. Reuse: recorded with the speaker's agreement; no names.

## Limits

- A course demo, not an FDOT product. Built from v1.5 (June 2025): confirm with District 7
  that it is still the current version before anyone relies on it.
- Covers PDF pages 5-11 only. Damage assessment pages and Appendix A are not included.
- Appendix B (zone maps) and Appendix C (responsibility matrix) are blank in v1.5, so the
  skill will not name zones, priority intersections or contacts.
- Every card is a draft for the signal team. Decisions the SOP gives to a person stay with
  that person ("Person decides: yes").
- Lessons and practice are suggestions. They never become SOP steps.
