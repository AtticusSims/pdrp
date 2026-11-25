---
id: C02
title: Explicit Negative-Coverage Map yields judge-invariant +12.5 pp unanswerable
  abstention gain with 31% fewer tokens
type: claim
temporal_status: current
source_locators:
- article:196-202
- article:214-235
- article:304-306
- supplement_s1:113-124
- supplement_s1:180-195
relations:
- type: uses
  target: M01
  basis: Layer-0 Negative-Coverage Map + Cycle 2 Bounded Absence Confirmation
- type: derived_from
  target: D01
  basis: 8 verified unanswerable questions x 8 models = 64 matched pairs
linked_cards:
- Q03
- Q04
- M01
---

# C02: Explicit Negative-Coverage Map yields judge-invariant +12.5 pp unanswerable abstention gain with 31% fewer tokens

The protocol's single most durable, judge-invariant, and multiplicity-safe improvement over strong Okapi BM25 search emerged on verified unanswerable abstention queries (8 plausible questions verified absent from the entire archive x 8 models = 64 matched pairs; article:214-224, supplement_s1:113-124). Declaring verified archival gaps upfront inside the strictly bounded (<2.5 KB) Layer-0 Negative-Coverage Map raised clean abstention accuracy from 73.4% under raw BM25 to 85.9% under both Cycle 1 and Cycle 2 (+12.5 percentage points, +8 paired wins / 0 losses, exact McNemar p = 0.0078). Adding Cycle 2's Bounded Absence Confirmation rule (limiting verification to at most one targeted BM25 search when the manifest flags an item absent) preserved the full +12.5 pp accuracy win while slashing median unanswerable-query token budgets by 31% (115,747 vs. 166,547 tokens under raw search, two-sided Wilcoxon p = 0.0329; supplement_s1:122). Crucially, this abstention advantage survives Holm-Bonferroni multiplicity correction (p_adj = 0.039), question-clustered Wilcoxon testing across the 8 independent queries (p = 0.0312), both single judges identically (+12.5 pp, p = 0.0078 under Judge A GLM-5.3 and Judge B Kimi-K2.5 alike), and exclusion of dual-role models Grok 4.6 and DeepSeek V3.2 (+14.6 pp, +7/-0, p = 0.0156; supplement_s1:129-140, 180-187). This anchors Design Principle 1 (DP1).
