# Skills we want

Pick one, then open a *Skill proposal* issue so others know you are building it. Ideas not
on this list are welcome too. Each row names a job, not just a document.

Before you start, check the **reuse** column: it decides what you may copy into the skill
(see the Sources table in [CONTRIBUTING.md](CONTRIBUTING.md)).

## Manuals and standards

| Suggested name | The job | Main source | Reuse |
|---|---|---|---|
| `mutcd-provision-lookup` | Find the MUTCD provisions that apply to a device or a situation and quote them by section and paragraph, keeping Standard, Guidance, Option and Support apart. | MUTCD 11th Edition (FHWA) | public domain (U.S. federal work) |
| `signal-warrant-check` | Check intersection counts against the MUTCD Chapter 4C signal warrants, with every threshold in code. The engineering study and the decision stay with an engineer. | MUTCD 11th Edition, Chapter 4C | public domain (U.S. federal work) |
| `work-zone-layout-check` | Check a temporary traffic control layout against MUTCD Part 6: taper lengths, sign spacing, buffer space, all computed in code. | MUTCD Part 6; FDOT Standard Plans Index 102 | public domain; check FDOT's terms |
| `fdot-design-manual-lookup` | Find the FDOT Design Manual section for a design question and quote it with its chapter and date. | FDOT Design Manual (current year) | public agency document; check FDOT's terms |

## Safety data and vehicle technology

| Suggested name | The job | Main source | Reuse |
|---|---|---|---|
| `nhtsa-complaint-reader` | Read NHTSA vehicle complaints (flat files or API): what each field means, component codes, finding ADAS-related complaints, counting by make, model and year without double counting. | NHTSA Office of Defects Investigation complaints data | public domain (U.S. federal work) |
| `nhtsa-sgo-crash-reader` | Read Standing General Order crash reports for ADAS and automated driving: field meanings, what is redacted, and which comparisons across manufacturers are not valid. | NHTSA Standing General Order data | public domain (U.S. federal work) |
| `crash-narrative-coder` | Code crash narratives into a codebook's categories, with "unsure" and the words that decided each code. | Your codebook; public narratives only | depends on the codebook |

## Simulation and operations

| Suggested name | The job | Main source | Reuse |
|---|---|---|---|
| `sumo-run-and-check` | Build, run and check a SUMO scenario before reporting results: warm-up, teleports, insertion backlog, and GEH against counts. Uses [sumo-agent-tools](https://github.com/ai4mobility/sumo-agent-tools). | SUMO documentation | check SUMO's license |
| `wzdx-feed-check` | Check a work zone data feed: spec version, required fields, records past their end date, missing lane data. Uses [WZDx-Tools](https://github.com/ai4mobility/WZDx-Tools). | WZDx specification (USDOT) | check the specification's license |
| `fundamental-diagram-fit` | Fit a fundamental diagram to detector data and report capacity, critical density and wave speed, with the fit's limits. | Textbook relationships (cite them) | cited only |

## Agency practice

| Suggested name | The job | Main source | Reuse |
|---|---|---|---|
| `survey123-form-fill` | Answer an agency's field form with its exact menu choices, one question at a time, with "unsure". The form-file method from AI for Mobility. | The agency's form definition | permission from the agency |
| `post-storm-damage-codes` | Classify signal or roadway damage from photos into an agency's damage codes, with "unsure" and the evidence. | The agency's damage scale | permission from the agency |

## Research methods

| Suggested name | The job | Main source | Reuse |
|---|---|---|---|
| `transportation-ai-paper-check` | Read a transportation AI paper and check its data, baselines, metrics and simulation-to-real gaps before citing it. | Your checklist, with the papers it comes from | cited only |
