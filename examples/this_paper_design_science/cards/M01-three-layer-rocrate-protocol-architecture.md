---
id: M01
title: Three-layer RO-Crate PDRP architecture, Gericke method elements, and software
  forcing function
type: method
temporal_status: current
source_locators:
- article:78-124
- supplement_s1:8-69
relations:
- type: uses
  target: U01
  basis: Cycle 2 procedural rules over identical 3-layer packaging
linked_cards:
- Q04
- U01
- C04
---

# M01: Three-layer RO-Crate PDRP architecture, Gericke method elements, and software forcing function

Grounded in Blessing & Chakrabarti's (2009) Design Research Methodology and Gericke, Eckert & Stacey's (2022) five method elements (Table 2, article:82-91), the study specifies two coupled PDRP artifacts: a Runtime Disclosure Protocol and a four-stage Pre-Publication Authoring Workflow. Packaged via the RO-Crate 1.1 JSON-LD profile (forward-compatible with RO-Crate 1.3, Sefton et al. 2026), the runtime protocol comprises three layers satisfying Design Requirements DR1-DR4 (article:96-113; supplement_s1:8-19): (1) Layer 0 (Compact Entry Manifest, COMPANION.md strictly <=2,500 B / ~600 tokens) preloaded alongside the untouched main article, containing a scope header, an explicit Negative-Coverage Map of verified absent records, a flat 1-line-per-card directory, and SHA-256 checksums in ro-crate-metadata.json; (2) Layer 1 (16-18 Atomic Evidence Cards, 140-320 words each) anchored to exact Layer-2 line ranges with typed relations (supports, qualifies, derived_from, uses, conflicts_with, responds_to, updates), where read_card() enforces bidirectional software co-retrieval of linked Qualification and Update cards as a Norman (2013) forcing function; and (3) Layer 2 (Immutable Primary Archive) accessed identically across raw and companion arms via Okapi BM25 search_corpus (k1=1.5, b=0.75; 1.5% zero-hit rate vs. ~66% preliminary substring search) and bounded read_source with an article alias. A worked verbatim specimen from Hippocampal Ripples (eLife 111304) appears in article:112 and supplement_s1:31-69.
