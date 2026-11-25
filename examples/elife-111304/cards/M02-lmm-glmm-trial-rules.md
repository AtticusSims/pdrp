---
id: M02
title: LMM and GLMM specifications, trial inclusion rules, and permutation tests
type: method
temporal_status: peer_review_revision
source_locators:
- article:264-287
- article:297-297
- author_response:135-156
- author_response:238-246
- author_response:319-323
relations:
- type: supports
  target: C02
  basis: Poisson GLMM and three-way interaction specifications
linked_cards:
- Q03
- U02
- D01
---

# M02: LMM and GLMM specifications, trial inclusion rules, and permutation tests

Stage-averaged ripple rates (events/s) were computed per trial across pre-encoding baseline (–800 to –200 ms relative to stimulus onset), encoding (0–3 s; sensitivity check 0–1 s), maintenance (3–10 s), and retrieval (probe onset to response) (`article:267`, `author_response:259`). Stage comparisons used linear mixed-effects models (LMMs) in R `lme4` with a four-level `stages` fixed effect and random intercepts for participant and trials nested within participant, followed by pairwise estimated marginal means (`emmeans`) contrasts corrected via Benjamini–Hochberg FDR (`article:269-271`, `author_response:319-323`).

Fine-grained time-series analyses binned ripples in non-overlapping 100 ms windows smoothed with a 400 ms Gaussian kernel, tested against baseline or between conditions (remembered vs. forgotten; fast vs. slow via per-subject median RT) using two-tailed non-parametric cluster-based permutation tests (5,000 label permutations, `α=0.05`) with MATLAB code archived at `https://doi.org/10.5281/zenodo.10877825` (`article:93, 273`).

Maintenance ramping was modeled via generalized linear mixed-effects models (GLMMs) with a **Poisson link function** on trial-level ripple counts (correcting inconsistent preprint "logistic" wording; `article:279-281`, `author_response:146-150`), entering 7 s maintenance `time`, `memory` (remembered=1, forgotten=0, or fast vs. slow), and random participant intercepts/time slopes plus nested trial intercepts. Because equations were stripped from extracted `article.txt:270, 280, 286, 288` (and `article:287` contains a copy-paste typo naming `test_type` for `region`), exact three-way formulas appear ONLY in `author_response`:
- Regional dissociation (`author_response:154`): `Ripple rate ~ 1 + time × memory × region + (1 + time | participant) + (1 + participant | trial)`
- VSTM vs. LTM dissociation (`author_response:240`): `ripple ~ time × memory × test_type + (1 + time | participant) + (1 | participant: trial)`

Group-level validation fitted linear regressions to each patient's mean maintenance ripple-rate time series and tested slopes with t-tests (`article:283`). Trial inclusion (`author_response:135-144`, `article:87, 103, 128, 297`): stage LMMs and ramping GLMMs included ALL trials (preserved when restricting to ripple-present maintenance trials, `p_FDR<0.001`); coupled-ripple analyses used only HPC-ripple-present trials, supplemented by 1,000× trial-count-matched bootstrapping (`p=0.017`).
