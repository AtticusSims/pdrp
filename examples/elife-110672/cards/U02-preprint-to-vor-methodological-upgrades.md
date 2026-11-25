---
id: U02
title: 'Preprint-to-VOR methodological upgrades: PELT calibration, mismatches, and
  terminology'
type: update
temporal_status: peer_review_revision
source_locators:
- public_reviews:16-19
- author_response:23-25
- author_response:37
- author_response:49-55
- article:173-177
- article:203-207
- article:386
relations:
- type: updates
  target: C01
  basis: Added IVT PELT framework and 10×200k background checks
- type: updates
  target: M02
  basis: Added basecalling-mismatch audit across modifications
- type: updates
  target: M03
  basis: Replaced X-fold placeholder with 1.5-fold (log2 > 0.585)
linked_cards:
- Q03
- Q04
---

# U02: Preprint-to-VOR methodological upgrades: PELT calibration, mismatches, and terminology

Comparing `public_reviews:19` and `author_response:23-55` against the published VOR documents four major methodological and terminological upgrades introduced during peer review that distinguish the VOR from earlier preprint versions:

1. **IVT-based PELT calibration framework:** Introduced to justify modification probability cutoffs (≥0.98 for m6A, ≥0.99 for Ψ and inosine) quantitatively against unmodified IVT RNA rather than relying on visual inspection alone. In the final minor revision, Reviewer #2 caught an unreplaced placeholder ('at least X-fold more signal') and warned against equating `log2 = 1.5` with `1.5-fold` enrichment; the authors updated Methods (`article:386`) to specify 1.5-fold enrichment (`log2 ratio > 0.585`).
2. **Multi-threshold background-signal evaluation:** Added 10-iteration × 200,000-read BBMap subsampling with mixed-effects statistics across cumulative cutoffs (0.5–0.99) and discrete probability intervals.
3. **Basecalling-mismatch audit:** Added analysis of non-reference basecalls at filtered sites (`article:203-207`, Fig 2—figure supplement 17), exposing C-biased mismatches at Ψ and G-biased mismatches at inosine.
4. **Terminology standardization:** Replaced 'stoichiometry' with 'predicted modification proportion', removed 'unbiased' descriptions of thresholding, and replaced 'false-positive' with 'background signal' for this study's own metrics (retaining 'false-positive' only when quoting prior publications)—though isolated legacy wording remains in figure legends and `supp2` (`Q04`).
