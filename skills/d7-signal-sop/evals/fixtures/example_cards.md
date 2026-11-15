<!-- Example output for scenario_day1.md. Written while building the kit, by Claude
(claude-opus-5-5) following the d7-signal-sop skill. Your live run will word things
differently. Run:  python check_cards.py scenario/example_cards.md -->

### Card 1: Sort the 31 US-19 signals by ATMS color
- **Do:** Treat the 18 green signals as operational and confirm they show in eSTORM. Put the 6 yellow (in flash) and 7 red (non-operational) signals on the list for SAT and generator teams.
- **Who:** not stated (Appendix C is blank)
- **When:** now (07:30)
- **SOP:** Post-Storm > Immediately Post Storm > 1.1.2 — "All operational (green) signals in the ATMS signal system should be fully reflected in eSTORM."; Post-Storm > Immediately Post Storm > 1.2.1 — "A yellow or red status in the ATMS signal system should be used to help prioritize SAT and generator deployment teams."
- **Weight:** standard
- **Person decides:** no

### Card 2: Set the order for the next generators
- **Do:** Decide whether generators go only to Priority #1 intersections or to every red signal in the zone. The agent cannot rank the 7 red signals: the SOP has no priority list and the zone maps are blank.
- **Who:** TMC personnel
- **When:** before the next generator leaves the yard
- **SOP:** Pre-Storm > Three Hours Prior > 2.2 — "TMC personnel to determine generator deployment priorities"
- **Weight:** standard
- **Person decides:** yes — TMC personnel; the SOP gives them this decision

### Card 3: Log the two deployed generators
- **Do:** Record team name, generator number and deployment time for NH-114 (06:10, US-19 @ Gulf to Bay) and NH-121 (06:40, US-19 @ Drew St).
- **Who:** not stated (Appendix C is blank)
- **When:** now
- **SOP:** Post-Storm > Immediately Post Storm > 3.1 — "Assign generators to teams and document: team name, generator NH #, and time/date deployed."
- **Weight:** standard
- **Person decides:** no

### Card 4: Refuel NH-114 by 12:10 and NH-121 by 12:40
- **Do:** Send the refueling team to NH-114 first (due 12:10), then NH-121 (due 12:40). Times from `rules.py refuel`.
- **Who:** not stated (Appendix C is blank)
- **When:** 2026-10-10 12:10 and 12:40
- **SOP:** Post-Storm > Immediately Post Storm > 3.2.1 — "First refueling to occur six (6) hours after initial deployment"
- **Weight:** standard
- **Person decides:** no — later refuels follow fueling needs (3.2), which a person sets

### Card 5: Run SAT passes at 09:00 and 14:00
- **Do:** Send SATs along their assigned corridors at 09:00 and 14:00 today. Times from `rules.py sat`.
- **Who:** Situational Awareness Teams (SAT)
- **When:** 2026-10-10 09:00 and 14:00
- **SOP:** Post-Storm > Immediately Post Storm > 6.1 — "SAT assessments will continue twice daily at 9:00 AM and 2:00 PM"; Post-Storm > 0-1 Week Post Storm > 1 — "SAT assessments shall continue daily at 9:00 AM and 2:00 PM"
- **Weight:** must
- **Person decides:** no

### Card 6: Keep eSTORM current and download it every hour
- **Do:** Enter each SAT finding in eSTORM as soon as it comes in, and download the eSTORM data every hour.
- **Who:** SAT for updates; not stated for the hourly download (Appendix C is blank)
- **When:** continuous; downloads at 08:00, 09:00, 10:00 ...
- **SOP:** Post-Storm > Immediately Post Storm > 6.3 — "eSTORM updates shall be made as soon as possible."; Post-Storm > Ongoing Efforts > 1.1 — "Download eSTORM data each hour to keep historical track of changes."
- **Weight:** must
- **Person decides:** no

### Card 7: Photograph damage with GPS
- **Do:** For every damaged signal, take pictures with GPS location as part of the detailed assessment.
- **Who:** Situational Awareness Teams (SAT)
- **When:** during each SAT pass
- **SOP:** Post-Storm > Immediately Post Storm > 6.4 — "Detailed assessments, including pictures of damage with GPS locations."
- **Weight:** standard
- **Person decides:** no

### Card 8: Watch signals come back on commercial power
- **Do:** Use Duke Energy's outage map to see which red signals regain power, then check in ATMS that each one runs correctly. Report any still in flash.
- **Who:** not stated (Appendix C is blank)
- **When:** continuous
- **SOP:** Post-Storm > Immediately Post Storm > 4.1 — "Use outage maps provided by power companies."; Post-Storm > Immediately Post Storm > 5 — "Confirm signals are operating correctly upon power restoration."
- **Weight:** standard
- **Person decides:** no

### Card 9: Consider asking DAT to report devices missing from eSTORM
- **Do:** If DAT is deployed, consider asking them to report signals, speed feedback signs and beacons they find that are not in eSTORM.
- **Who:** DAT personnel
- **When:** when DAT deploys
- **SOP:** Post-Storm > Immediately Post Storm > 7 — "Consider requesting them to report signals, speed feedback signs, and beacons that are not found in eSTORM."
- **Weight:** consider
- **Person decides:** no

### Not covered
- Which zone each red signal is in, and the priority routes: Appendix B (zone maps) is blank in v1.5. Ask arterial RTMC.
- Who owns logging, refueling and downloads: Appendix C (responsibility matrix) is blank. Ask the D7 signal lead.
- An emergency TWO on Nov 9: `rules.py two 2026-11-09 2026-11-08` says no, the executive order expired Nov 8 (TWO 12).
