---
id: C03
title: Token efficiency follows an archive-scale crossover from -21%/-34% savings
  at 60 files to +49% overhead at 37 KB
type: claim
temporal_status: current
source_locators:
- article:196-203
- article:307-309
- supplement_s1:104-112
- results_report:127-147
relations:
- type: derived_from
  target: D01
  basis: 4 frozen corpora spanning 37 KB to 1.08 MB supplementary scale
- type: uses
  target: M02
  basis: 128 trials per study per arm across all 8 models
linked_cards:
- D01
- Q03
---

# C03: Token efficiency follows an archive-scale crossover from -21%/-34% savings at 60 files to +49% overhead at 37 KB

Disaggregating median total token consumption across the four multidisciplinary archives exposed a sharp, judge-independent corpus-scale efficiency crossover that grounds Design Principle 2 (DP2; article:202, 307-309; supplement_s1:104-112). On the largest, most heterogeneous archive (Computational Aesthetics, 60 supplementary files totaling 1.08 MB), progressive disclosure improved accuracy over both raw search (59.4% vs. 57.0%) and full-card preloading (58.6%) while cutting median tokens by 26% in Cycle 1 (46,974 vs. 63,794) and 21% in Cycle 2 (50,617) against raw BM25, and by 34% (Cycle 1) to 29% (Cycle 2) against full-card preloading (71,488 tokens). On the two mid-sized heterogeneous archives (Hippocampal Ripples: 5 files, 125 KB; Creative-Coding Review: 8 files, 181 KB), the protocol improved accuracy (78.1% to 85.9% and 67.2% to 68.0%) at essentially neutral token cost (0% to +7% change vs. raw BM25). Conversely, on the smallest archive (Nanopore RNA Calibration, 37 KB dominated by compact CSV tables), calibrated BM25 already reached 84.4% clean success, and layered summary reading added +59% (Cycle 1) to +49% (Cycle 2) token overhead (89,566 and 83,951 vs. 56,300 tokens) via double-reading. Local open-weight models pooled across all 4 papers likewise incurred a small statistically significant Cycle 2 token increase (54,653 vs. 52,741, p = 0.0057; article:225).
