---
id: U01
title: Telemetry-driven Cycle 1 to Cycle 2 procedural redesign over byte-identical
  corpora and cards
type: update
temporal_status: cycle2_refinement
source_locators:
- article:118-124
- article:204-209
- supplement_s1:14-16
- supplement_s1:113-124
relations:
- type: updates
  target: M01
  basis: Refines runtime read_card payload, verification footer, and absence search
    bound
- type: supports
  target: C04
  basis: Documents exact 3 procedural changes separating Cycle 1 from Cycle 2
linked_cards:
- M01
- C04
- C05
---

# U01: Telemetry-driven Cycle 1 to Cycle 2 procedural redesign over byte-identical corpora and cards

Forensic error inspection of every discordant Cycle 1 trial where raw BM25 beat Cycle 1 isolated three behavioral flaws rather than factual errors inside cards (article:204-209): (1) Compression substitution accounted for nearly one-third of Cycle 1 losses (e.g., all Inkling 2 Small losses had zero hallucinations/overclaims yet omitted one verbatim phrase or secondary statistic by stopping at a summary card instead of opening a short peer-review letter); (2) Unnecessary card calls on self-contained article-only queries inflated token volume (+58% median tokens vs. raw BM25 in Cycle 1, 52,818 vs. 33,477; supplement_s1:118); and (3) Redundant multi-turn confirmation searches on items already declared absent in Layer 0 kept unanswerable token budgets near raw search (165,477 vs. 166,547; supplement_s1:122). Cycle 2 (PDRP v3.1) held all 4 corpora, all 68 cards, every manifest, and all 64 questions 100% byte-identical while modifying only three protocol mechanisms (article:118-124, supplement_s1:15): adding the Article-Sufficiency Gate (trimming article-only tokens -24% vs. Cycle 1), stripping YAML headers (~30-34% smaller payloads) with top-2 Q/U co-retrieval and a deterministic [VERIFY_PRIMARY_SPANS] footer for spans <=80 lines, and capping absent-item re-checks to at most one BM25 query (-31% abstention tokens).
