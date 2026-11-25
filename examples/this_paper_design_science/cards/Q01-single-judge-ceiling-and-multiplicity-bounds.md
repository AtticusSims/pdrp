---
id: Q01
title: Single-judge ceiling sensitivity and Holm-Bonferroni multiplicity bounds separating
  durable vs. narrow margins
type: qualification
temporal_status: current
source_locators:
- article:226-228
- article:286-288
- supplement_s1:180-195
relations:
- type: qualifies
  target: C01
  basis: All-8 Cycle 2 vs Raw flips to -0.4 pp (p=0.90) under Judge A alone
- type: qualifies
  target: C04
  basis: Frontier-4 vs Raw narrows to +1.6 pp (p=0.45) under Judge A alone and Holm
    p_adj=0.093
- type: qualifies
  target: M03
  basis: Strict AND-consensus amplifies borderline disagreements near ceiling
linked_cards:
- C01
- C04
- D02
---

# Q01: Single-judge ceiling sensitivity and Holm-Bonferroni multiplicity bounds separating durable vs. narrow margins

Re-running every primary contrast independently under our best-calibrated single judge (Judge A GLM-5.3, post-stratified kappa = 0.794, -0.3 pp bias) and applying Holm-Bonferroni multiplicity correction across key contrasts separates durable findings from judge-sensitive margins (article:286-288, supplement_s1:180-195). Five empirical conclusions remain statistically significant under Judge A alone, Judge B alone, AND strict consensus (with top contrasts surviving Holm adjustment): (1) Cycle 2 vs. Manuscript Only (+35.9 pp consensus, +36.7 pp Judge A, p < 10^-45); (2) Unanswerable Abstention Cycle 2 vs. Raw BM25 (+12.5 pp, p = 0.0078 identically across all three; Holm p_adj = 0.039); (3) DeepSeek V3.2 Reasoning ON recovery (+12.5 pp consensus, +15.6 pp Judge A) and Gate DiD(C2-C1) (+23.4 pp consensus, p = 0.0039; Holm p_adj = 0.023; +25.0 pp Judge A, p = 0.0018); (4) Qwen 3.8 27B OFF 52-trial zero-error lead (+13.5 pp consensus, p = 0.0156; +11.5 pp Judge A, p = 0.0312); and (5) post-hoc Unified All-5 Cloud Reasoning-ON (+5.6 pp consensus, p = 0.0014; Holm p_adj = 0.010; +4.4 pp Judge A, p = 0.0161; +5.3 pp Judge B, p = 0.0033). However, narrower contrasts do NOT reach significance under Judge A alone: aggregate All-8 Cycle 2 vs. Raw BM25 (-0.4 pp, p = 0.9036), Frontier-4 Cloud Cycle 2 vs. Raw BM25 (+1.6 pp, p = 0.4545; Holm p_adj = 0.093), and post-hoc All-8 Unified Reasoning-ON (+2.5 pp Judge A, p = 0.1421; vs. +4.5 pp consensus, p = 0.0076), because Judge A already scored strong Okapi BM25 near ceiling (94.5% on Frontier-4).
