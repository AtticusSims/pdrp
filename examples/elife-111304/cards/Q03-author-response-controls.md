---
id: Q03
title: Author-response control analyses and response-vs-article discrepancies
type: review_disposition
temporal_status: peer_review_revision
source_locators:
- author_response:99-102
- author_response:139-144
- author_response:225-230
- author_response:259-261
- author_response:351-358
- author_response:374-376
- author_response:396-398
- article:113-113
- supp1:11-26
relations:
- type: responds_to
  target: Q01
  basis: 1/f slope and raw IPI checks address noise and artifact concerns
- type: qualifies
  target: D02
  basis: LTL slopes promised in response are absent from supp1
linked_cards:
- M01
- M02
- U02
---

# Q03: Author-response control analyses and response-vs-article discrepancies

The 104 KB `author_response` contains **four substantive reviewer-requested control analyses that do NOT appear in `article.txt`**:
1. **Aperiodic 1/f background control (`author_response:99-102`, Author response image 1):** Addressing Reviewer #2's concern citing van Schalkwijk & Helfrich (2026) that awake MTL ripple detections can reflect 1/f noise modulations, the authors quantified aperiodic slope across the 7 s delay and found no significant temporal ramp (`p>0.600`) and no remembered vs. forgotten difference (`p=0.544`).
2. **Ripple-present-only ramping control (`author_response:139-144`, Author response image 3):** Restricting the maintenance GLMM exclusively to trials with ≥1 detected HPC ripple preserved the significant ramping-up effect (`p_FDR<0.001`), ruling out bias from zero-ripple trials.
3. **Probe-onset-locked retrieval alignment (`author_response:351-358`, Author response image 5):** Re-aligning retrieval HPC ripple rates to probe onset (rather than motor response) reproduced the significant ripple suppression ~1–2 s post-probe.
4. **LTM-stratified VSTM behavioral check (`author_response:225-230`, Author response image 4):** Median-splitting the 13 patients on LTM cued-recall accuracy (median 0.45; Poor LTM `n=7` vs. Good LTM `n=6`) showed no VSTM accuracy difference (`t(11)=–1.20, p=0.254`).

Additionally, `author_response` supplies exact numbers missing from `article.txt` (HFA slope `β=0.002` at `200`; tuned 0–1 s encoding p-values at `259`; explicit GLMM formulas at `154, 240`) and exposes **two factual discrepancies** between the response letter and final files: (a) `author_response:376` claims participant-level LTL ramping slopes were added to Table S1, but `supp1:11-26` contains LTL channel counts only (no LTL β column); and (b) `author_response:398` states ripple-rate variability did not significantly differ between HPC and LTL, whereas `article:113` (Fig 3—fig supp 1j) actually reports significantly *greater* HPC than LTL SD (`ps_cluster<0.032`), with the `time × region` interaction surviving SD adjustment (`p=0.017`).
