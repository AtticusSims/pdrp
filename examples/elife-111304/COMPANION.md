# Companion: Ramping-up hippocampal ripples and their neocortical coupling support human visual short-term memory
DOI: 10.7554/eLife.111304 | VOR: 2026-11-20 | CC-BY-4.0 | 3 reviewed preprints -> VOR v1

## Coverage Map
- **Only in `author_response`:** 4 omitted controls (1/f slope, ripple-only trials, probe-lock, LTM split), GLMM formulas, HFA beta=0.002, 0-1s encoding p-values, preprint "solid" assessment, revision log.
- **Only in `supp1` & `mdar`:** Per-patient HPC/LTL/AMY/PHC/ERC channels, HPC slopes, trials (N=3,444); MDAR: Liu 2020 reanalysis, no preregistration, power calc, or blinding.
- **Only in `elife_assessment_and_versions` & `public_reviews`:** "solid"->"convincing" upgrade, editors, Reviewers #1-#3 VOR caveats (HFA, AMY+ERC, LTM, >1s semantics).
- **Absent:** Raw iEEG traces, trial decoding matrices, OSF files/URL, healthy controls, load/delay/lure manipulations, saccades, per-patient age/sex/meds/SOZ/hemisphere, LTL slopes.

## Card Index
- C01 [claim] Stage HPC/LTL ripple rates & null accuracy | baseline, novelty, RT, LMM
- C02 [claim] HPC ramping predicts VSTM vs LTL | ramping, GLMM, accuracy, gray-matter
- C03 [claim] Coupled ripples predict VSTM, no lag/ramp | 50ms, bootstrap, lag, uncoupled
- C04 [claim] Coupled ripples lock LTL decoding | SVM, 1.85-2.25s, reactivation
- C05 [claim] VSTM ripples dissociate from LTM | cued-recall, p=0.071, median-split
- D01 [data] Cohort, trial imbalance & MDAR | N=13, 3444-trials, blinding, power
- D02 [data] Per-patient HPC, LTL & MTL electrodes | 69-HPC, 132-LTL, AMY, PHC, ERC
- M01 [method] iEEG preprocessing, IEDs & detectors | bipolar, 70-180Hz, IPI, 80-120Hz
- M02 [method] LMM/GLMM specs & trial rules | Poisson, lme4, emmeans, 5000-perms
- M03 [method] Coupling windows, SVM & surrogates | 500ms, 50ms, Morlet, LOTO
- Q01 [qualification] Epilepsy cohort, HFA & MTL gaps | HFA, p=0.662, AMY, ERC
- Q02 [qualification] Ramping paradox, lag & task limits | paradox, load, saccades, semantic
- Q03 [review_disposition] Response controls & discrepancies | 1/f, probe-lock, trial-filter
- Q04 [review_disposition] Reviewers #1-#3 VOR caveats | sa1, sa2, sa3, Norman-2019
- U01 [update] Preprint->VOR & assessment upgrade | versions, solid, convincing
- U02 [update] Preprint v1->VOR analytical changes | interactions, Poisson, Dickey
