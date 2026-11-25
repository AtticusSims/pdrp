---
id: C02
title: Dorado increasingly recovers high-proportion GLORI m6A sites
type: claim
temporal_status: original_article
source_locators:
- article:219-242
- article:292
- article:306
- author_response:19-21
- author_response:45-47
relations:
- type: uses
  target: M04
  basis: Matched-input GLORI protocol and intersection filter
- type: derived_from
  target: D03
  basis: GLORI sequencing depth and conversion rates
linked_cards:
- Q02
- U01
---

# C02: Dorado increasingly recovers high-proportion GLORI m6A sites

To compare Dorado (DRACH and all-context, v0.9.0) directly against chemical-conversion GLORI on the same poly(A) RNA input, the authors restricted both methods to sites covered by ≥20 reads, present in both DMSO and STM2457 samples, and exhibiting >10% predicted m6A/A proportion in DMSO (plus Dorado A≥0.8, m6A≥0.98; GLORI p≤0.05). Under this shared-condition filter, Dorado detected 81,012 all-context and 72,372 DRACH sites in NHDFs (77,728 and 67,222 in HD10.6), whereas GLORI detected 140,934 all-motif vs 27,926 DRACH sites in NHDFs (174,282 vs 27,965 in HD10.6). The 113,008 non-DRACH GLORI calls in NHDFs contributed virtually no additional overlap with Dorado.

Comparing NHDF high-confidence GLORI DRACH sites against Dorado DRACH calls across ascending predicted m6A/A proportion thresholds showed sharply rising recovery of GLORI sites by Dorado: 13,614 shared sites at ≥10% (48.8% of 27,926 GLORI DRACH sites, though only 18.8% of 72,372 Dorado DRACH sites; `author_response:45-47`), 11,536 at ≥20% (nearly 70%), 6,307 at ≥50% (almost 90%), and 3,119 at ≥80% (>93%). Read-coverage distributions were similar between shared and GLORI-only categories, whereas GLORI-only calls clustered predominantly in the 10–20% stoichiometry bin. Because all four GLORI libraries achieved ~95% gene-wide A-to-I conversion (below the 98–99% benchmark), GLORI provides complementary rather than complete orthogonal validation; HD10.6 overlap percentages are not separately reported.
