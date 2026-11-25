---
id: M02
title: Four-paper zero-contamination testbed, 64 card-blind questions, and 2,880-trial
  cumulative design matrix
type: method
temporal_status: current
source_locators:
- article:126-159
- supplement_s1:20-30
- supplement_s1:70-87
relations:
- type: uses
  target: D01
  basis: 4 frozen multidisciplinary archives and 8 reader models
linked_cards:
- D01
- Q04
- Q02
---

# M02: Four-paper zero-contamination testbed, 64 card-blind questions, and 2,880-trial cumulative design matrix

To test cross-disciplinary generalization while preventing pretraining memorization, the evaluation testbed pairs two unpublished internal manuscripts (Computational Aesthetics and Creative-Coding Review) with two external CC-BY-4.0 Versions of Record published in eLife on 20 November 2026—the day before benchmark execution (Liu, Jing et al. 2026, eLife 15:RP111304; Ohnezeit et al. 2026, eLife 15:RP110672; article:130-142). Companion authoring followed four quality gates: isolated Gemini 4 Neon drafting, deterministic schema validation (4/4 crates passed with 0 errors), adversarial line-by-line auditing by DeepSeek V3.2 (0 high-severity defects, 5 minor surgical edits), and timed side-by-side author sign-off (article:114-117). To avoid circular evaluation, Grok 4.6 authored all 64 questions strictly from raw Layer-2 archives without ever accessing manifests or cards, balanced evenly across 4 papers x 4 obligations (16 each: Article-Only, Supplementary Fact, Qualification Binding, and Temporal Evolution [8] + Unanswerable Abstention [8]), each with 2-4 immutable source-anchored rubric criteria (article:143-147). Cumulative execution totaled 2,880 controlled reading trials across four phases (Table 4, article:149-157): Cycle 1 main (1,536 trials: Manuscript Only, Raw BM25, Cycle 1), Full-Card Preload ablation on 2 multi-file papers (256 trials), Cycle 2 redesign over byte-identical cards (512 trials; main subtotal N = 2,304), and the isolated 3-model within-weight reasoning toggle experiment (576 trials).
