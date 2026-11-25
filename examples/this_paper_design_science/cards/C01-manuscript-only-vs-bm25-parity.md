---
id: C01
title: PDRP beats manuscript-only reading by 35.9 pp while staying near aggregate
  parity with strong BM25
type: claim
temporal_status: current
source_locators:
- article:176-202
- article:214-230
- results_report:6-35
- supplement_s1:180-195
relations:
- type: uses
  target: M02
  basis: 512 matched model-by-question trials per arm across 4 studies
- type: derived_from
  target: D01
  basis: 8 cloud and local reader models over 64 card-blind questions
linked_cards:
- Q01
- M02
- D01
---

# C01: PDRP beats manuscript-only reading by 35.9 pp while staying near aggregate parity with strong BM25

Across all 512 matched model-by-question pairs in the pre-specified default fleet (Table 5, Panel A), supplying the main manuscript in isolation achieved only 38.7% strict consensus clean success (95% CI 34.6-43.0%), collapsing to 0.0% on supplementary fact extraction and 1.6% on temporal evolution while incurring 13.7% hallucinations and 39.3% unwarranted abstentions (article:176-201). Layering the refined Cycle 2 Progressive-Disclosure Research Protocol (PDRP) over the same frozen archives raised verified accuracy to 74.6% (95% CI 70.7-78.5%), a +35.9 percentage-point gain (+193 wins / -9 losses, exact McNemar p < 10^-45; Holm p < 10^-44; question-clustered 95% CI [+27.0, +44.9 pp]) holding across both single judges individually (Judge A +36.7 pp; Judge B +36.5 pp; supplement_s1:180-186). Against calibrated Okapi BM25 over untouched supplements (71.7% clean success), the aggregate 8-model Cycle 2 margin was modest (+2.9 pp, +43/-28, p = 0.0959; article:214-224), yet stratifying Table 5 (Panel B) by default reasoning state shows Cycle 2 beat or matched both raw search and Cycle 1 on every accuracy and safety column across all 7 native reasoning-enabled models (77.5% clean, 92.1% rubric, 2.9% overclaim, 4.0% hallucination, 0.9% wrong abstention; see Q01 for Judge A sensitivity).
