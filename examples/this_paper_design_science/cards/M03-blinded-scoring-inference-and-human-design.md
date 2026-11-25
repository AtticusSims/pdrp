---
id: M03
title: Zero-overlap cross-family blinded judging, confirmatory/multiplicity inference,
  and two-task human validation
type: method
temporal_status: current
source_locators:
- article:160-169
- article:268-289
- supplement_s1:85-87
- supplement_s1:161-195
relations:
- type: uses
  target: D02
  basis: 68/68 author crate audit and 180-item stratified human calibration
linked_cards:
- D02
- Q01
- Q03
---

# M03: Zero-overlap cross-family blinded judging, confirmatory/multiplicity inference, and two-task human validation

All 2,880 reading responses were stripped of model names, condition tags, tool traces, and token counts prior to grading by two independent zero-overlap cross-family judges: Judge A (z-ai/glm-5.3) and Judge B (moonshotai/kimi-k2.5), totaling 5,760 API calls with zero judge errors (article:160-164, supplement_s1:85-87). Primary outcome Strict Consensus Clean Success requires both judges independently to pass every atomic rubric item with zero overclaim, hallucination, or wrong-abstention flags (inter-judge Cohen's kappa = 0.820 clean / 0.885 atomic in main benchmark; 0.746 in reasoning ablation). Matched model-by-question pairs used two-sided exact McNemar binomial tests (binary accuracy) and two-sided Wilcoxon signed-rank tests (difference-in-differences and token counts). Three primary confirmatory contrasts were pre-specified (Cycle 2 vs. Manuscript Only, Cycle 2 vs. Raw BM25 overall, and Cycle 2 vs. Raw BM25 on unanswerable abstention), supplemented by Holm-Bonferroni adjustment across key contrasts, question-clustered 95% bootstrap CIs, and full single-judge checks (article:164-166, supplement_s1:180-195). Human validation ran in a unit-tested blind local workbench across Task 1 (side-by-side crate audit: original author on both internal manuscripts, non-author reader on both external eLife studies) and Task 2 (180 stratified blind grades split 50/50 between 90 AI-unanimous [92.3% prevalence] and 90 AI-disagreement [7.7% prevalence, 6.5x oversampled] trials, evaluated via Horvitz-Thompson post-stratification with 5,000-draw stratified bootstrap CIs and two-sided Fisher exact condition-bias tests; article:166-169).
