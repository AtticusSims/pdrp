---
id: C05
title: Within-weight reasoning toggles expose architecture-dependent fragility of
  natural-language bypass gates (DP5)
type: claim
temporal_status: current
source_locators:
- article:239-267
- article:316-318
- reasoning_ablation_report:1-20
- supplement_s1:180-195
relations:
- type: uses
  target: M02
  basis: 576 isolated within-weight ablation trials across 3 clean-switch architectures
- type: supports
  target: M01
  basis: Motivates moving conditional sufficiency gates into deterministic code
linked_cards:
- Q02
- U01
- M03
---

# C05: Within-weight reasoning toggles expose architecture-dependent fragility of natural-language bypass gates (DP5)

In Cycle 2, DeepSeek V3.2 (the sole cloud model defaulting to explicit reasoning disabled) dropped nearly 16 pp relative to Cycle 1 (70.3% -> 54.7%) because it exploited the natural-language Article-Sufficiency Gate to skip all tools on 15 of 16 qualification-binding questions (article:237, 247-263). Toggling reasoning modes within identical weights across all three clean-switch models (n = 576 isolated trials) revealed three distinct architectural responses rather than a uniform linear rule. First, inside DeepSeek V3.2, enabling explicit reasoning (effort=medium) causally eliminated bypass collapse: qualification zero-tool skips plunged from 15/16 to 0/16, Cycle 2 jumped to 73.4% vs. 60.9% raw BM25 (+12.5 pp, p = 0.0386; -27.1% median tokens, 143.6K vs. 197.1K), and the gated-vs-mandatory within-weight interaction DiD(Cycle 2 - Cycle 1) reached +23.4 pp (Wilcoxon p = 0.0039; Holm p_adj = 0.023; Judge A +25.0 pp, p = 0.0018), while extending the post-hoc reasoning-enabled pool across all 8 models (n = 512) lifted Cycle 2 to 77.0% vs. 72.5% raw (+4.5 pp, p = 0.0076) and vs. 73.6% Cycle 1 (+3.3 pp, p = 0.0498; supplement_s1:189-192). Second, local Qwen 3.8 27B inverted DeepSeek's pattern (0/16 opt-outs OFF at 89.1% vs. 4/16 ON at 79.7%; see Q02 for 40K GPU cap). Third, local GPT-OSS 20B hit a uniform tool-calling floor across all arms (6 -> 11/16 skips). Together, these trajectories establish DP5: natural-language bypass clauses exhibit unpredictable, architecture- and deliberation-dependent fragility and should be moved into deterministic client or server routing logic.
