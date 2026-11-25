---
id: D03
title: GLORI read/conversion metrics and SPEN isoform coverage table
type: data
temporal_status: original_supplement
source_locators:
- supp3_s1_Sheet1:1-6
- supp4_s1_Dorado_SPEN_isoforms:1-7
- article:242
- article:248
- article:340
relations:
- type: derived_from
  target: M04
  basis: GLORI NovaSeq 6000 sequencing and conversion outputs
- type: supports
  target: C02
  basis: Documents ~95% GLORI gene-wide A-to-I conversion rates
- type: supports
  target: C04
  basis: Quantifies Dorado read coverage across SPEN isoforms
linked_cards:
- Q02
- Q01
---

# D03: GLORI read/conversion metrics and SPEN isoform coverage table

Two compact supplementary CSV tables supply exact GLORI library metrics (`supp3_s1_Sheet1`) and Dorado SPEN isoform read coverage (`supp4_s1_Dorado_SPEN_isoforms`) omitted from the main text.

**GLORI sequencing & A-to-I conversion (`supp3_s1_Sheet1`):**
- `NHDF_DMSO`: 90,131,613 sequenced; 65,244,375 mapped (72.39%); Overall Gene Conversion (CR) = **0.953**.
- `NHDF_STM2457`: 89,460,291 sequenced; 66,532,504 mapped (74.37%); CR = **0.948**.
- `HD10.6_DMSO`: 76,182,834 sequenced; 59,162,958 mapped (77.66%); CR = **0.954**.
- `HD10.6_STM2457`: 63,784,945 sequenced; 49,389,099 mapped (77.43%); CR = **0.951**.
Notably, `article:340` states '>80 million reads per sample', whereas both HD10.6 GLORI libraries fall below 80M reads (76.18M and 63.78M), and all four CR values (94.8–95.4%) fall below the 98–99% benchmark cited from Shen et al. (2024).

**Dorado SPEN isoform coverage (`supp4_s1_Dorado_SPEN_isoforms`, gene `ENSG00000065526.13`):**
- `SPEN-201` (`ENST00000375759.8`, 12,385 nt): coverage = **108**.
- `SPEN-202` (`ENST00000438066.2`, 13,500 nt): coverage = **90**.
- `SPEN-207` (`ENST00000704274.1`, 8,040 nt): coverage = **5**.
- `SPEN-206` (`ENST00000673875.1`, 3,123 nt): coverage = **1**.
- `SPEN-203` (`ENST00000442985.1`, 891 nt): coverage = **0**.
Only 5 of SPEN's 7 annotated isoforms appear in `supp4`, and only SPEN-201 and SPEN-202 pass the ≥20-read threshold (54.5% vs 45.5% of the two detected isoforms). No equivalent isoform coverage tables are exported for `KRTAP1-5`, `HSPA8`, or `CITED2`.
