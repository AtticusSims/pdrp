---
id: C04
title: Coupled ripples selectively lock late-encoding LTL category reactivation
type: claim
temporal_status: peer_review_revision
source_locators:
- article:136-138
- article:150-174
- article:303-313
- author_response:277-315
relations:
- type: uses
  target: M03
  basis: broadband SVM decoding and ripple-locked surrogate tests
- type: supports
  target: C03
  basis: links maintenance coupled ripples to cortical reinstatement
linked_cards:
- Q02
- Q04
- M03
---

# C04: Coupled ripples selectively lock late-encoding LTL category reactivation

Linear SVM decoders trained on broadband (2–180 Hz) LTL spectral power classify the four object categories above 25% chance on remembered trials across encoding, early maintenance, and retrieval clusters (`ps_cluster<0.039`) and stage averages (`ps_FDR<0.003`; `article:153`). Maintenance decoding is not solely lingering visual offset: 1 s maintenance bins 1, 3, and 4 all exceed chance (`ps_FDR<0.042`; `article:163`). Forgotten trials also decode above chance in stage averages (`ps_FDR<0.037`); remembered decoding exceeds forgotten only in a pre-response retrieval cluster (`p_cluster=0.012`; encoding trend `p_cluster=0.064`; stage averages `ps_FDR>0.258`; `article:163`).

Aligning continuous LTL decoding (±0.5 s) to HPC peaks of pooled HPC–LTL coupled ripples (439±125/patient) against 1,000 non-coupled surrogates identifies a significant positive reactivation cluster specifically for classifiers trained on **late encoding (1.85–2.25 s post-stimulus; `p_cluster=0.029`)** (`article:170`). Evaluated within that cluster, coupled ripple-locked LTL reactivation is significant during **maintenance (`p_cluster=0.004`)**—and above 25% chance (`all ps<0.002`)—but non-significant during encoding and retrieval (`ps_cluster>0.118`). Direct cross-stage contrasts show maintenance exceeds retrieval (`p_cluster=0.024`) but does NOT significantly exceed encoding (`ps_cluster>0.800`; `article:170`, `author_response:293`).

Specificity controls confirm coupled-ripple selectivity: HPC decoding exceeds chance in stage averages (`ps_FDR<0.038`) yet is NOT time-locked to coupled ripples (`ps_cluster>0.470`), and neither HPC nor LTL decoding is locked to uncoupled HPC (`ps_cluster>0.222`) or uncoupled LTL ripples (`ps_cluster>0.203`; `article:168, 172`). Across the 7 s maintenance interval, the 1.85–2.25 s decoder shows a `time × VSTM accuracy` interaction (`p=0.009`), reflecting significant decay on forgotten trials (`p_FDR=0.031`) versus stability on remembered trials (`p_FDR=0.214`); coupled ripple-locked decoding itself shows no significant ramp (`p=0.586`; `article:138, 174`).
