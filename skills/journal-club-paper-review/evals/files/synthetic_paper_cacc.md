<!-- SYNTHETIC PAPER, written only to test the journal-club-paper-review skill. It is not a
real publication; the authors, journal and numbers are invented, and it contains planted
problems that the tasks in evals.json check for. -->

# Cooperative Adaptive Cruise Control Eliminates Freeway Stop-and-Go Waves: A Comprehensive Simulation Study

A. Rivera, B. Chen, C. Okafor. *Journal of Synthetic Transportation Studies*, 12(3), 2026.

[p. 1]

## Abstract

In today's rapidly evolving transportation landscape, cooperative adaptive cruise control
(CACC) plays a pivotal role in seamless traffic operations. This paper delves into the
effect of CACC on freeway congestion. We propose a novel CACC controller and evaluate it in
SUMO on a freeway segment with an on-ramp. Results show that CACC reduces average delay by
32% and eliminates stop-and-go waves. The results are validated with real-world field
data. The findings provide comprehensive, robust and actionable insights for agencies.

## 1. Introduction

Stop-and-go waves waste fuel, raise crash risk and cut throughput at freeway bottlenecks.
Connected and automated vehicles may damp these waves, because they react to the vehicles
ahead faster than people do.

No previous study has examined CACC in mixed traffic with human drivers.

The contributions of this paper are:
- C1. A novel CACC controller for mixed traffic (Sec. 3).
- C2. Evidence that CACC reduces average delay at 50% market penetration (Sec. 5).
- C3. Validation of the simulation results with real-world field data (Sec. 4).

[p. 2]

## 2. Literature review

Earlier work studied CACC string stability in platoons of automated vehicles only. Two
studies, Study X (2019) and Study Y (2022), simulated CACC vehicles mixed with human
drivers on a freeway and found smaller delay benefits at low penetration rates. Their
networks did not include an on-ramp.

[p. 3]

## 3. Controller

Each CACC vehicle keeps a constant time gap to its leader:

a(t) = k1 (gap(t) - s0 - h v(t)) + k2 (v_lead(t) - v(t)), with h = 0.6 s, k1 = 0.23,
k2 = 0.07, and s0 = 2 m.

Human drivers follow SUMO's default Krauss model. This is the constant-time-gap form
widely used for CACC; the novelty is the choice of gains for an on-ramp merge.

[p. 4]

## 4. Simulation setup and validation

The network is one 5-km, three-lane freeway segment with one on-ramp at km 3. Demand is
one hour: 5,200 veh/h on the mainline and 900 veh/h on the ramp. CACC market penetration
is 0%, 50% or 100%. Each scenario was run once with random seed 42.

To validate the simulation, we compared the 0% scenario with SUMO's default parameter
values and found that average speeds agreed within 3%. No field data were used.

[p. 5]

## 5. Results

Table 2. Average delay per vehicle (s/veh).

| CACC penetration | Delay (s/veh) | Change from 0% |
|---|---|---|
| 0% | 41.2 | - |
| 50% | 33.8 | -18% |
| 100% | 30.9 | -25% |

Fig. 3 (time-space diagram, described): the number of stop-and-go waves passing km 2
during the hour falls from 14 at 0% penetration to 6 at 50% and to 0 at 100%.

[p. 6]

## 6. Conclusions

CACC eliminates stop-and-go waves and reduces delay substantially at all penetration
levels. Agencies should plan for CACC deployment on congested freeways. Future work
should use more data.
