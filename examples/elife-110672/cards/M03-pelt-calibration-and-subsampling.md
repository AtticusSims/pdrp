---
id: M03
title: Two-stage PELT change-point calibration and subsampled background ratio
type: method
temporal_status: peer_review_revision
source_locators:
- article:173-175
- article:369-378
- article:383-398
- author_response:53-55
- mdar:99-100
relations:
- type: uses
  target: M02
  basis: Operates on Modkit v0.4.1 sample-probs histograms
- type: supports
  target: C01
  basis: Derives 0.98 m6A and 0.99 Ψ/inosine probability cutoffs
linked_cards:
- Q04
- U02
---

# M03: Two-stage PELT change-point calibration and subsampled background ratio

To derive modification probability thresholds empirically against unmodified IVT RNA, the authors built a two-stage statistical framework in R v4.4.2 (RStudio 2024.12.1+563; packages `changepoint`, `dplyr` v1.1.4, `ggplot2` v3.5.1, `reshape2` v1.4.4, `patchwork` v1.3.0, `data.table`, `scales`, `tidyr`; scripts at `github.com/DepledgeLab/HOLDEN`). For each probability bin, relative enrichment is computed as `log2(sample/IVT)` of modification probability fractions after adding a `1×10^-6` pseudocount, making the metric invariant to total sample read depth.

In Stage 1, the Pruned Exact Linear Time (PELT) algorithm detects change points along the binned log2-ratio series using a manual penalty of `1.0` and minimum segment length of `3` bins; the first change point marks the boundary between the IVT-indistinguishable baseline and signal emergence. In Stage 2, the modification probability cutoff is defined as the first bin at or after that change point exceeding 1.5-fold enrichment (`log2 ratio > 0.585`). Uncertainty is quantified via 95% bootstrap confidence intervals from 2,000 bin resamples with replacement.

Separately, empirical background-call ratios across cumulative cutoffs (0.5, 0.7, 0.9, 0.98, 0.99) and discrete probability bins were quantified by subsampling aligned BAMs to 200,000 reads across 10 independent random seeds (`sampleseed=1–10`) via BBMap v39.01 `reformat.sh`, comparing IVT-to-sample call ratios with linear mixed-effects models (sample random effect, Benjamini–Hochberg correction).
