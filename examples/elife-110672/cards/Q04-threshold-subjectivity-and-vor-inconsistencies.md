---
id: Q04
title: Threshold subjectivity, background-ratio semantics, and residual VOR mismatches
type: qualification
temporal_status: peer_review_revision
source_locators:
- author_response:23-25
- author_response:49-55
- article:66
- article:74
- article:89
- article:94
- article:109-119
- article:229
- article:386
- supp2_s1_Sheet1:3-29
relations:
- type: qualifies
  target: M03
  basis: PELT cutoff relies on manual penalty and enrichment choice
- type: qualifies
  target: M02
  basis: Empirical IVT/sample ratio is not a formal FPR
- type: qualifies
  target: C01
  basis: Residual false-positive and log2 legend discrepancies in VOR
- type: qualifies
  target: D02
  basis: supp2 retains stoichiometry labels and lacks HD10.6 IVT
linked_cards:
- U02
---

# Q04: Threshold subjectivity, background-ratio semantics, and residual VOR mismatches

Two conceptual caveats raised during review plus three residual inconsistencies in the published VOR warrant caution when citing thresholds or metrics from this study.

First, Reviewer #1 established that the PELT thresholding procedure is **not 'unbiased'**: it depends on manual parameter choices (penalty `1.0`, minimum segment length `3` bins, `1×10^-6` pseudocount) and a predetermined 1.5-fold enrichment rule, so it should be described strictly as data-driven or empirically calibrated against matched unmodified controls (`author_response:23-25`). Second, Reviewer #2 noted that the IVT-to-sample call ratio is an **empirical background-call ratio**, not a formal false-positive rate (FPR), because ground-truth modification status and testability at every site are unknown (`author_response:49-51`).

Third, four concrete residual inconsistencies persist inside the VOR files despite review corrections: (1) Methods (`article:386`) and `author_response:55` correctly equate 1.5-fold enrichment to `log2 ratio > 0.585`, whereas Figure 2A (`article:74`) and Figure 2—figure supplements 4A, 7, 8, and 9 (`article:94, 109, 114, 119`) still print the erroneous label `log2≥1.5 fold` / `log2≥1.5-fold`; (2) Results heading `article:66` retains 'removes false positives' and `supp2_s1_Sheet1` headers retain 'stoichiometry' despite the VOR shift to 'background signal' and 'predicted modification proportion'; (3) Figure 2—figure supplement 3 (`article:89`) and Figure 3—figure supplement 1C (`article:229`) captions mislabel HD10.6 plots as NHDFs; and (4) `supp2` includes IVT counts only for NHDF HG38, not HD10.6 or Gencode47.
