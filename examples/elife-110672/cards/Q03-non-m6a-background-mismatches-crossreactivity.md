---
id: Q03
title: High Ψ/I background, m5C failure, basecall mismatches, and cross-reactivity
type: qualification
temporal_status: original_article
source_locators:
- article:177-179
- article:193-195
- article:203-207
- article:213
- article:302
- supp2_s1_Sheet1:29-36
- supp2_s1_Sheet1:54-58
relations:
- type: qualifies
  target: C01
  basis: m6A filtering success does not transfer cleanly to Ψ/I/m5C
- type: qualifies
  target: C05
  basis: Neighboring mods and basecall errors perturb DRS signal
- type: qualifies
  target: M02
  basis: Model drift across Remora versions and mismatch exclusion
- type: qualifies
  target: D02
  basis: Unexpected STM2457 m5C drop and inosine rise in supp2
linked_cards:
- U02
---

# Q03: High Ψ/I background, m5C failure, basecall mismatches, and cross-reactivity

Dorado's calibration performance degrades markedly outside m6A. For Ψ and inosine, even at the stricter ≥0.99 modification probability cutoff, subsampled IVT-to-sample background ratios remain high (~20–30%, vs <5% for all-context m6A at ≥0.98), and unfiltered IVT inosine calls persist above 50% predicted proportion. For **m5C**, DMSO, STM2457, and IVT probability distributions are indistinguishable and **no valid filter could be established** (`article:177`). Moreover, `supp2_s1_Sheet1` reveals an unexplained 60–69% drop in filtered ≥10% m5C calls under the METTL3 inhibitor STM2457 across all four sample/reference sets (e.g., NHDF HG38: 6,930 -> 2,130; HD10.6 HG38: 4,926 -> 1,708), underscoring m5C model unreliability.

High-probability inosine calls increase under STM2457 in genome-aligned probability distributions (NHDF HG38 ≥10%: 9,722 -> 14,263; HD10.6 HG38: 5,614 -> 14,288)—attributed to intron retention (absent from transcriptome-aligned probability profiles, though `supp2` Gencode47 ≥10% counts also rise: 7,828 -> 11,809 and 3,897 -> 8,049) or model misclassification.

Three structural caveats further qualify all Dorado proportions: (1) Modkit excludes mis-basecalled reads, deletions, alternative mods, and motif-disrupting errors from valid coverage; sites with ≥25% non-reference basecalls skew strongly toward **C** at Ψ and **G** at inosine, risking underestimated proportions or missed sites; (2) citing Diensthuber et al. (2026), Dorado Ψ cross-reacts with m1Ψ, m5C with hm5C/ac4C, and nearby mods alter signal; (3) model updates shift calls (v5.0.0 generates many unique low-confidence all-context m6A and Ψ sites absent in v5.1.0), requiring re-benchmarking per release.
