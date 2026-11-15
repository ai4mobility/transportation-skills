# Transportation checks

Not in the guide [S2]. Use them as prompts where they apply to the paper; do not force all
of them onto every paper, and do not present them as the guide's requirements.

- **Field data.** Where, when, for how long, and how many vehicles, trips or crashes? One
  corridor, one city, one season? How was ground truth obtained?
- **Safety.** Crashes are rare. If surrogate measures (TTC, PET, DRAC) stand in for
  crashes, are the thresholds justified, and is exposure accounted for?
- **Simulation** (SUMO, VISSIM, Aimsun, cellular automata). Calibrated and validated
  against which field data? How many random seeds? Is the demand realistic?
- **Vehicle technology** (ADAS, CAV, EV). Which market penetration rates, which driver and
  vehicle differences, which controller settings? Are the results sensitive to them?
- **Traffic flow.** Are the results consistent with known traffic behavior (capacity,
  capacity drop, wave speeds)? Are stability claims tested on platoons, not one vehicle?
- **Machine learning.** Is the train/test split by time and place, so the same
  corridor-day is not in both? Are there strong simple baselines (historical average, last
  value, a well-tuned classical model)? Do the metrics match the operational need? Results
  over several seeds?
- **Practice.** Could an agency or consulting firm use this? Do they have the data, the
  compute and the staff to keep it running?
