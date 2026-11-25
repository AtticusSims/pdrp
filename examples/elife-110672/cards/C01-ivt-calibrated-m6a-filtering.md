---
id: C01
title: IVT-calibrated thresholds remove Dorado m6A background signal
type: claim
temporal_status: original_article
source_locators:
- article:171-183
- article:189-191
- article:294-298
- supp2_s1_Sheet1:5-16
- supp2_s1_Sheet1:42-48
relations:
- type: uses
  target: M02
  basis: Dorado v0.9.0 and Modkit v0.4.1 pileup
- type: uses
  target: M03
  basis: PELT change-point calibration against IVT
- type: derived_from
  target: D02
  basis: Exact filtered vs unfiltered site counts in supp2
linked_cards:
- Q01
- Q03
- Q04
- U02
---

# C01: IVT-calibrated thresholds remove Dorado m6A background signal

Benchmarking Oxford Nanopore Technologies (ONT) direct RNA sequencing (DRS) with Dorado v0.9.0 (model v5.1.0) against unmodified in vitro transcribed (IVT) poly(A) RNA and 48-hour 30 µM STM2457 (METTL3 inhibitor) treatment establishes four best-practice filters for high-confidence m6A calling: canonical adenosine basecall probability ≥0.8 (met by 75–90% of A calls), modification probability ≥0.98, reference-matched adenosine with ≥20 valid reads, and predicted m6A/A proportion ≥10%.

Below 0.98 modification probability, DMSO, STM2457, and IVT distributions are effectively identical. In unfiltered genome-aligned NHDF data (≥20 reads, all proportions), the all-context model calls 11.5× more sites than DRACH-context (6,212,071 vs 539,170), and most calls lie below 10% predicted proportion (92% all-context, 75% DRACH; <1% exceed 50%). Applying the ≥0.98 and ≥10% filters removes >70% of calls, collapsing the all-context vs DRACH ratio to 1.14× (134,701 vs 118,374 in NHDF HG38) while retaining STM2457-sensitive sites (NHDF DRACH drops 90.7% to 10,997; all-context drops 88.5% to 15,545).

In NHDF HG38 IVT controls (≥10%), filtering reduces background calls from 14,145 to 264 (all-context) and from 93 to 3 (DRACH). Across 10 × 200,000-read subsamples, IVT-to-NHDF background drops from ~35% (≥0.5) to <5% (≥0.98/0.99) for all-context m6A, and starts ~10% (≥0.5) for DRACH. The standard Enolase II RNA calibration strand (RCS) spike-in yields comparable probability profiles and serves as a built-in negative control.
