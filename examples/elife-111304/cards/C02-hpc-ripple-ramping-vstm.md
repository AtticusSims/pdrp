---
id: C02
title: Maintenance HPC ripple ramping predicts VSTM accuracy and dissociates from LTL
type: claim
temporal_status: peer_review_revision
source_locators:
- article:98-122
- supp1:11-26
- author_response:139-156
- author_response:252-255
relations:
- type: uses
  target: M02
  basis: Poisson GLMM and 3-way regional interaction
- type: derived_from
  target: D02
  basis: per-patient HPC/LTL channel counts and HPC slopes
linked_cards:
- Q01
- Q02
- Q03
---

# C02: Maintenance HPC ripple ramping predicts VSTM accuracy and dissociates from LTL

Across the 7 s maintenance delay, an all-trial Poisson GLMM reveals progressive ramping-up of HPC ripple counts (`β=0.012, z=4.678, p<0.001`; `article:101`). Adding VSTM accuracy yields a significant `time × accuracy` interaction (`β=0.018, z=2.171, p=0.030`), driven by robust ramping on remembered trials (`β=0.014, z=5.024, p_FDR<0.001`) and no slope on forgotten trials (`β=–0.002, z=–0.282, p_FDR=0.778`; `article:103`). Conventional participant-level linear regressions replicate this effect (`supp1:11-26`, `article:113`, `author_response:252`): 11/13 patients show positive HPC β on remembered trials (range –0.134 to 0.503; negative only in Sub1 –0.134 and Sub12 –0.061; `t(12)=3.580, p=0.004`), whereas 4/13 show positive slopes on forgotten trials (–0.257 to 0.228; `t(12)=–0.669, p=0.516`), with remembered slopes exceeding forgotten slopes (`t(12)=3.400, p=0.005`, higher in 11/13 patients).

The accuracy-dependent HPC ramp persists across all sensitivity checks: ripple duration ≥25 ms (`time × accuracy β=0.033, z=2.983, p=0.003`), alternative 80–120 Hz / ≥25 ms / >3 SD Vaz criteria (`β=0.024, z=3.281, p=0.001`), and restriction to trials containing ≥1 maintenance ripple (`p_FDR<0.001`; `article:113`, `author_response:139-144`). HPC ramping is invariant to retrieval speed (fast `β=0.010, p_FDR=0.014`; slow `β=0.018, p_FDR<0.001`; interaction `p=0.117`) and item novelty (novel `β=0.018, p_FDR<0.001`; repeated `β=0.009, p_FDR=0.003`; interaction `p=0.086`; `article:113, 120`).

By contrast, LTL ripples show no overall ramp (`β=–0.005, z=–1.772, p=0.076`), no `time × accuracy` interaction (`β=–0.010, z=–1.246, p=0.213`), no RT interaction (`p=0.277`), and null group-level slopes (`t(12)=–0.707, p=0.493`; `article:113, 122`). A direct three-way `time × accuracy × region` GLMM confirms regional dissociation (`β=0.053, z=2.012, p=0.044`; `article:122`, `author_response:154-156`). Restricting LTL to 89 gray-matter bipolar pairs yields a reversed interaction (`β=–0.020, p=0.043`) driven by a remembered-trial *decrease* (`β=–0.009, p_FDR=0.017`; `article:113`). Controlling for larger HPC than LTL ripple-rate SD (`ps_cluster<0.032`) preserves the `time × region` interaction (`p=0.017`; `article:113`). Note: HPC ripple ramping did not significantly differ from broadband 70–180 Hz HFA ramping (`p=0.662`; `article:101`, `author_response:200`; see `Q01`).
