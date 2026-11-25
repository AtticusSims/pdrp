---
id: U02
title: Concrete analytical, statistical, and reporting changes from preprint v1 to VOR
type: update
temporal_status: peer_review_revision
source_locators:
- author_response:39-45
- author_response:110-156
- author_response:200-335
- author_response:366-398
- supp1:1-42
relations:
- type: updates
  target: M02
  basis: corrected Poisson GLMM wording and added formal interaction models
- type: updates
  target: M03
  basis: separated 500ms lead-lag normalization from 50ms coupled ripples
- type: updates
  target: C03
  basis: added stage ANOVA, peak-lag tests, and maintenance dynamics
linked_cards:
- U01
- Q03
- D02
---

# U02: Concrete analytical, statistical, and reporting changes from preprint v1 to VOR

Point-by-point comparison of `author_response` with the VOR (`article`, `supp1`) documents four concrete categories of preprint-to-VOR revisions:

1. **Terminology, citations, and model-specification fixes:** Separated the broad ±0.5 s cross-correlation window (relabeled "Normalized LTL ripple rate (z-score)" in Fig 4b, citing Dickey et al., 2022 instead of miscited spindle-ripple studies) from "coupled ripples" reserved strictly for ±50 ms overlap (Vaz et al., 2019; `author_response:43, 265-269`). Corrected inconsistent preprint "logistic" vs. "Poisson" GLMM descriptions to Poisson (`author_response:146-150`), explicitly explained `emmeans` pairwise contrasts with Benjamini–Hochberg FDR (`author_response:319-323`), and clarified trial inclusion (all trials for stage/ramping models; HPC-ripple-present trials for coupling; `author_response:137`).
2. **Formal interaction models replacing p-value comparisons:** Added three-way `time × memory × region` GLMM (`β=0.053, z=2.012, p=0.044`; `author_response:154-156`), three-way `time × memory × test_type` GLMM (`β=0.039, z=1.809, p=0.071`; `author_response:240-246`), coupled-ripple `stage × accuracy` ANOVA (`F(2,24)=0.49, p=0.619`; `author_response:273`), and direct maintenance vs. retrieval (`p_cluster=0.024`) and maintenance vs. encoding (`ps_cluster>0.800`) decoding contrasts (`author_response:293`).
3. **New validation and trajectory analyses:** Added raw-trace IPI check (89.84±3.31% in 70–180 Hz; Fig 2—fig supp 1a), 70–180 Hz HFA comparison (`β=0.002, p=0.074`; slope diff `p=0.662`), tuned 0–1 s encoding stage contrasts (Fig 2—fig supp 4), peak-to-peak lag tests (`ps_FDR>0.069`), coupled vs. uncoupled LTL split (Fig 4—fig supp 2), maintenance trajectories for coupled ripples (`p=0.506`), decoding (`p=0.009`), and ripple-locked decoding (`p=0.586`; Fig 4—fig supp 1), plus four response-only controls (`Q03`).
4. **Figures, Methods, and Tables:** Replaced single-channel exemplar raster with group Fig 2b (unified y-axis, pink ramping arrow), added group-averaged Fig 2a waveform/spectrum, drew Fig 2d cluster bar, converted Fig 5a/c heatmaps to accuracy/normalized accuracy, added full 13-patient rasters (Fig 2—fig supp 3), participant-level swarm plot (Fig 3—fig supp 1b), expanded LTM/IED/bootstrapping Methods, and added `supp1` Tables A–B (though promised LTL slopes remain absent from `supp1:11-26`).
