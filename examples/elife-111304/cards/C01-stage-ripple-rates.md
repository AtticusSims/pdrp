---
id: C01
title: Task-stage HPC and LTL ripple rates and null VSTM accuracy contrasts
type: claim
temporal_status: peer_review_revision
source_locators:
- article:71-95
- article:267-273
- author_response:257-261
- author_response:351-358
relations:
- type: uses
  target: M01
  basis: ripple detection and raw IPI validation
- type: uses
  target: M02
  basis: stage LMM and cluster permutation tests
linked_cards:
- Q01
- Q03
- U02
---

# C01: Task-stage HPC and LTL ripple rates and null VSTM accuracy contrasts

Across all 13 epilepsy patients (69 HPC, 132 LTL channels) and all task stages, mean HPC ripple rate is 0.29 event/s (Hz; `article:85`). HPC ripples occur in 54.26±13.55% of trials during encoding (0–3 s), 78.74±13.25% during maintenance (3–10 s), and 26.85±11.27% during pre-retrieval; corresponding LTL trial incidences are 32.17±14.69%, 52.34±17.82%, and 14.99±10.30% (`article:87, 91`). Encoding replicates the novelty effect: first-presentation items elicit higher HPC ripple rates than repeated presentations at 500–1100 ms post-stimulus (`p_cluster<0.001`; `article:73, 85`).

In all-trial LMMs relative to pre-encoding baseline (–800 to –200 ms), stage-averaged ripple rates rise significantly during encoding and retrieval in both HPC (`ps_FDR<0.009`) and LTL (`ps_FDR<0.002`), whereas stage-averaged maintenance does not differ from baseline in either HPC (`β=0.141, z=2.462, p_FDR=0.079`) or LTL (`β=–0.008, z=–2.505, p_FDR=0.059`; `article:87, 91`). Using the full 0–3 s encoding window, HPC retrieval exceeds encoding (`β=0.042, z=7.203, p_FDR<0.001`) and maintenance (`β=0.046, z=8.018, p_FDR<0.001`), while encoding and maintenance do not differ (`β=0.005, z=0.822, p_FDR=0.844`); in a reviewer-requested tuned 0–1 s encoding window (`author_response:259`), encoding exceeds baseline and maintenance in both regions (`ps_FDR<0.001`), HPC encoding matches retrieval (`p_FDR=0.859`), and LTL encoding remains below retrieval (`p_FDR=0.001`).

Time-resolved 100 ms cluster tests reveal elevated HPC ripples in early encoding (0.15–0.85 s, `p_cluster=0.018`) and late maintenance (7.85–8.15 s and 8.65–9.45 s, `ps_cluster<0.034`), followed by a post-response drop (0.05–1.0 s, `p_cluster=0.001`, confirmed ~1–2 s post-probe in `author_response:355`); LTL rises only in early encoding (0.15–0.55 s, `p_cluster=0.047`; `article:89, 91`). Critically, mean ripple rates do NOT separate VSTM remembered vs. forgotten trials in any stage in HPC (`ps_cluster>0.466`) or LTL (`ps_cluster>0.274`; `article:73, 93`). Faster remembered trials show higher HPC rates 150–450 ms pre-response (`p_cluster=0.014`; LTL `ps_cluster>0.237`), and HPC rates predict LTM retrieval success 1600–1900 ms pre-response (`p_cluster=0.047`; `article:73, 93`).
