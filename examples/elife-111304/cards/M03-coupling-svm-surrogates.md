---
id: M03
title: Coupled-ripple windows, broadband SVM decoding, and surrogate locking
type: method
temporal_status: peer_review_revision
source_locators:
- article:290-313
- author_response:43-43
- author_response:265-283
relations:
- type: supports
  target: C03
  basis: separates 500ms lead-lag normalization from 50ms coupling
- type: supports
  target: C04
  basis: specifies broadband SVM and coupled-ripple surrogate locking
linked_cards:
- Q02
- Q04
- U02
---

# M03: Coupled-ripple windows, broadband SVM decoding, and surrogate locking

Following peer review, the authors separated two previously conflated inter-regional ripple windows (`article:293-295`, `author_response:43, 265-269`):
1. **Broad lead–lag window (±0.5 s; Dickey et al., 2022):** Across all HPC–LTL channel pairs per participant (restricted to HPC-ripple-present trials), LTL ripple rates were aligned to ±0.5 s around HPC ripple peaks and z-scored against 1,000 surrogate distributions built by drawing `n` random non-ripple HPC time points (no HPC ripple within ±0.5 s). Channel-pair averages were cluster-tested against zero within ±0.25 s (`article:293`).
2. **Coupled ripples (±50 ms; Vaz et al., 2019):** Strictly defined as LTL ripples temporally overlapping or occurring within ±50 ms of an HPC ripple peak, pooled across trials and channel pairs (439±125 events/patient; `article:295`). Peak-to-peak lag tests evaluated directional precedence within these ±50 ms pairs (`article:128, 145`).

To decode object categories (animals, fruits, electrical devices, furniture; chance 25%), broadband (2–180 Hz) spectral power was extracted from all HPC or all LTL channels per participant using 6-cycle complex Morlet wavelets (2–29 Hz in 1 Hz steps; 30–180 Hz in 5 Hz steps), downsampled to 100 Hz, and z-scored per frequency and channel across runs (`article:303`). Power was averaged within sliding 400 ms windows (50 ms increment) to form `frequency × channel` feature vectors for linear SVMs. Sixty decoders (one per encoding time window, 0–3 s) were trained and tested across all encoding, maintenance, and retrieval windows using leave-one-trial-out cross-validation, with cluster-based permutation tests against 25% chance (`article:305`).

For coupled ripple-locked reactivation (`article:311-313`, `author_response:277-283`), continuous decoding accuracy within ±0.5 s of coupled HPC ripple peaks was extracted per trial, z-scored against 1,000 random non-coupled-timepoint surrogates, and cluster-tested to identify the data-driven reactivation cluster (trained on 1.85–2.25 s late encoding), then evaluated against both surrogates and 25% chance. Identical surrogate tests were applied to uncoupled HPC or LTL ripples (>50 ms from ripples in the other region).
