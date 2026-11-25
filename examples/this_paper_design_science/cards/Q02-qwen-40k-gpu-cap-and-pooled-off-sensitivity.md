---
id: Q02
title: Qwen 3.8 27B 49K-to-40K GPU context-cap confound, crash-excluded Pooled-OFF
  collapse, and gate inversion
type: qualification
temporal_status: current
source_locators:
- article:158-159
- article:247-266
- article:331-332
- reasoning_ablation_report:6-20
- supplement_s1:78-84
- supplement_s1:192-195
relations:
- type: qualifies
  target: C05
  basis: Gate-Sensitivity Asymmetry is NOT monotonic across all architectures
- type: qualifies
  target: D01
  basis: Local 32 GB VRAM forced tightening Qwen 27B OFF from 49,152 to 40,960 tokens
linked_cards:
- C05
- D01
- U01
---

# Q02: Qwen 3.8 27B 49K-to-40K GPU context-cap confound, crash-excluded Pooled-OFF collapse, and gate inversion

Two hardware and behavioral qualifications tightly bound interpretation of the within-weight reasoning experiment (Table 7, article:158, 259-266, 331; supplement_s1:192-195). First, to maintain 100% GPU residency on a 32 GB RTX 5090 during non-thinking inference, local Qwen 3.8 27B ran at a 49,152-token context cap in its native ON arm but was tightened by 17% to 40,960 tokens in its OFF arm, triggering 9 Ollama HTTP 500 context-overflow crashes under raw BM25 versus 6 under Cycle 1 and 2 under Cycle 2. Consequently, raw BM25 did NOT intrinsically collapse on Qwen 27B OFF: restricted to the 52 common zero-error questions unaffected by overflows, raw search stayed virtually flat (78.8% ON vs. 76.9% OFF), while Cycle 2 genuinely rose to 90.4% (+13.5 pp, +7/-0, p = 0.0156; Judge A p = 0.0312; Judge B p = 0.0156) and avoided 7 of 9 memory overflows. Second, excluding Qwen 27B OFF's 11 raw-or-Cycle-2 overflow pairs from the Pooled-3-Models Reasoning-OFF arm narrows the pooled overall gain from +7.3 pp (p = 0.0488) to a non-significant +3.9 pp (n = 181, p = 0.2962 consensus; +2.2 pp, p = 0.6177 Judge A) and collapses Pooled-OFF unanswerable abstention from +20.8 pp (p = 0.18) to +5.0 pp (n = 20, p = 1.000). Third, Qwen 3.8 27B inverted DeepSeek V3.2's opt-out behavior (0/16 qualification skips OFF vs. 4/16 ON), proving DP5 cannot be claimed to occur identically whenever reasoning is disabled.
