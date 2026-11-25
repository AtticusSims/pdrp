---
id: C03
title: HPC-LTL coupled ripples predict VSTM accuracy without ramping or directional lag
type: claim
temporal_status: peer_review_revision
source_locators:
- article:125-147
- article:293-297
- author_response:110-131
- author_response:265-273
relations:
- type: uses
  target: M03
  basis: 50ms coupling definition and 1000x surrogate normalization
- type: supports
  target: C02
  basis: inter-regional coupling complements maintenance HPC ramping
linked_cards:
- Q02
- Q03
- U02
---

# C03: HPC-LTL coupled ripples predict VSTM accuracy without ramping or directional lag

To assess hippocampal–neocortical coordination, normalized LTL ripple rates aligned within ±0.5 s of HPC ripple peaks (z-scored against 1,000 non-ripple surrogates across HPC-ripple-present trials) exceed zero across all task stages (`p_cluster<0.011`) and within encoding, maintenance, and retrieval individually (`all ps_cluster<0.047`; `article:128`). Reserving the term "coupled ripples" strictly for LTL ripples overlapping or occurring within ±50 ms of HPC ripple peaks yields 439±125 coupled ripples per participant across the task (143±45 encoding, 274±76 maintenance, 23±6 retrieval; `article:145, 295`).

During maintenance, coupled ripple rates are significantly higher on remembered than forgotten trials (`t(12)=2.897, p_FDR=0.040`; `article:145`). Because remembered trials vastly outnumber forgotten trials (`supp1:28-42`), the authors ran a 1,000-iteration bootstrap resampling remembered trials to match each patient's forgotten count; the maintenance accuracy advantage remains significant (`p=0.017`; `article:145, 297`). No accuracy difference appears during encoding or retrieval (`ps_FDR>0.726`).

Three crucial null findings constrain mechanistic interpretation:
1. **No stage-specificity interaction:** A repeated-measures `stage × accuracy` ANOVA added in revision is non-significant (`F(2,24)=0.49, p=0.619`; `article:145`, `author_response:273`).
2. **No temporal lead–lag / directionality:** Peak-to-peak lag between HPC and LTL ripples shows no systematic precedence in any stage across all trials (`ps_FDR>0.126`) or coupled remembered trials (`ps_FDR>0.069`; `article:128, 145`, `author_response:122-131`), indicating near-zero synchrony rather than demonstrated HPC-to-LTL driving.
3. **No maintenance ramping of coupled ripples:** Across the 7 s delay, coupled ripple rates show no significant ramp on remembered or forgotten trials (`ps_FDR>0.281`) and no `time × memory` interaction (`p=0.506`; `article:138, 147`). Splitting remembered-trial LTL ripples reveals only a non-significant upward trend for HPC-coupled LTL ripples (`β=0.032, p=0.126`) versus a significant decline for uncoupled LTL ripples (`β=–0.014, p=0.026`; interaction trend `β=0.031, p=0.088`; `article:143`, `author_response:110`).
