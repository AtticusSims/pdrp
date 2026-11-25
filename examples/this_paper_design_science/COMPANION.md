# Companion: The Progressive-Disclosure Research Protocol (PDRP)
Author: Atticus Sims (ORCID: 0009-0009-2933-2344) | Design Science | 2026-11-25 | CC-BY-4.0

## Coverage Map
- **Only in `supplement_s1`:** Tool specs, archive-identifier key, eLife 111304 specimen, runtime caps, Tables S1-S5 (model/paper/task scores, Grok/DeepSeek exclusion, within-model qualification checks, arm-level calibration breakdown, Judge A/B, Holm-Bonferroni, All-8 ON & cluster CIs, 4 minor edits).
- **Only in `human_validation_report`, `reasoning_ablation_report`, `results_report`:** Raw 52-trial Qwen OFF splits, complete stratum McNemar/Wilcoxon tests, and raw calibration cell counts.
- **Absent:** Direct co-retrieval ON/OFF ablation over identical cards; multi-rater independent human calibration or non-author crate timing; 49K VRAM-matched Qwen 27B OFF; Anthropic/OpenAI cloud endpoints; multimodal/notebook/CAD tests; per-criterion checkboxes on 131/180 items.

## Card Index
- C01 [claim] Manuscript-only collapse vs BM25 parity | +35.9pp, +2.9pp, Table-5
- C02 [claim] Negative-Coverage Map abstention win | +12.5pp, p=0.0078, -31%-tok
- C03 [claim] Archive-scale token crossover & DP2 | 60-file, -26%/-34%, 37KB-cost
- C04 [claim] Cycle 2 redesign & cloud reasoners | byte-identical, +5.6pp, -17%-tok
- C05 [claim] Within-weight reasoning & DP5 | DeepSeek-DiD, Qwen-inv, All-8-ON
- M01 [method] 3-layer PDRP & Gericke elements | Layer-0/1/2, forcing-fn, Cycle-2
- M02 [method] 4-paper testbed & 2,880-trial matrix | eLife-VOR, 64-blind, 4-phases
- M03 [method] Cross-family judges & human design | GLM-5.3, Kimi-K2.5, Holm, kappa
- D01 [data] Frozen corpora & 8-model fleet | 37KB-1.08MB, 5-cloud, 3-local-GPU
- D02 [data] 68/68 crate audit & 180 calibration | 94.1%-as-is, 15m, kappa=0.794
- Q01 [qualification] Single-judge ceiling & multiplicity | Judge-A, Frontier-4, All-8
- Q02 [qualification] Qwen 40K GPU cap & Pooled-OFF | 9-overflows, n=52, +3.9pp-ns
- Q03 [qualification] Single-author validation & N=4 | sole-rater, bias-power, scope
- Q04 [qualification] Dual-role overlap & DP4 gap | Grok, DeepSeek, excl-check
- U01 [update] Cycle 1->2 redesign & forensics | compression-sub, 3-rules
