---
id: Q01
title: Epilepsy sample caveat, broadband HFA overlap, and absent non-HPC MTL controls
type: qualification
temporal_status: peer_review_revision
source_locators:
- article:101-101
- article:194-194
- article:227-227
- supp1:11-26
- mdar:148-150
- public_reviews:29-41
- author_response:91-102
- author_response:196-213
relations:
- type: qualifies
  target: C01
  basis: clinical epilepsy sample and broadband HFA overlap
- type: qualifies
  target: C02
  basis: ripple vs HFA slope ns and no AMY/ERC anatomical control
- type: qualifies
  target: M01
  basis: ripple specificity over 70-180 Hz HFA remains unresolved
linked_cards:
- D02
- Q03
- Q04
---

# Q01: Epilepsy sample caveat, broadband HFA overlap, and absent non-HPC MTL controls

Three major methodological and anatomical caveats bound interpretation of hippocampal ripple specificity:

1. **Clinical neurosurgical sample without healthy controls or formal design safeguards:** All 13 participants are patients with drug-resistant epilepsy implanted for clinical monitoring (`article:47, 227`), reanalyzed from Liu et al. (2020a) with no healthy intracranial control group, no preregistration, no a priori sample size calculation, and no blinding (`mdar:102-104, 148-150`). Although epileptogenic-zone channels and ripples within 50 ms of neurologist-marked IEDs were excluded (`article:243, 259`), per-patient medication regimens, seizure-onset zones, and hemispheric lateralization are not reported, and clinical electrode placement prevented evaluating frontal, parietal, or occipital VSTM cortices (`article:198, 200`).
2. **Unresolved distinction between sharp-wave ripples and broadband HFA:** Reviewers #2 and #3 questioned whether 70–180 Hz detections reflect physiological sharp-wave ripples rather than generic high-gamma/HFA population activation (`author_response:91, 196`). While raw-trace IPIs (89.84±3.31% in 70–180 Hz), 80–120 Hz Vaz criteria (`p=0.001`), and aperiodic 1/f slope checks (`p>0.600`, `p=0.544`) rule out sharp spike artifacts and 1/f noise drift (`author_response:95-102`), continuous 70–180 Hz HFA shows a marginal maintenance ramp (`β=0.002, p=0.074`) and **does NOT differ significantly in ramping slope from detected HPC ripples (`p=0.662`)** (`article:101`, `author_response:200`). Authors concede HPC ripples cannot yet be established as functionally distinct from general HFA (`article:194`), and Reviewer #2 characterizes the VOR as showing "solid evidence that hippocampal high-frequency activity ramps up" (`public_reviews:29`).
3. **Declined non-hippocampal MTL anatomical control:** Reviewer #3 emphasized testing amygdala (AMY) or pooled AMY+entorhinal cortex (ERC)—regions exhibiting high gamma without true sharp-wave ripples (`public_reviews:35, 41`; `author_response:196`). Authors declined due to sparse sampling (20 AMY across 9 patients, 6 PHC across 5, 2 ERC in 1; `supp1:11-26`, `author_response:206-209`), leaving intra-MTL anatomical specificity untested.
