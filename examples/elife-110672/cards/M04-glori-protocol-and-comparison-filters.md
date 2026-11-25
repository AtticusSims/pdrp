---
id: M04
title: Matched-input GLORI chemistry, Snakemake workflow, and comparison filters
type: method
temporal_status: original_article
source_locators:
- article:219
- article:332-342
- mdar:99-100
relations:
- type: uses
  target: M01
  basis: Uses remaining 2/3 of matched poly(A) RNA input
- type: supports
  target: C02
  basis: Produces orthogonal m6A dataset for Dorado comparison
- type: supports
  target: D03
  basis: Generates GLORI sequencing and conversion metrics
linked_cards:
- Q02
- D03
---

# M04: Matched-input GLORI chemistry, Snakemake workflow, and comparison filters

GLORI-sequencing was performed on the remaining two-thirds of the same TRIzol-isolated, Dynabeads poly(A)-selected RNA preparations used for nanopore DRS, following Shen et al. (2024) with minor modifications. Poly(A) RNA was fragmented at 94 °C for 2 min (NEB E6150S), subjected to glyoxal protection, chemically deaminated in 750 mM NaNO2 (16 °C for 8 hr followed by 4 °C for 6 hr), and deprotected in triethylammonium acetate–formamide buffer at 95 °C for 10 min.

Ligation-based libraries incorporated 5′ adapters carrying 11-nt unique molecular identifiers (UMIs; Liu et al., 2025), were PCR-amplified with NEBNext Dual Primers Set 2 (E7780S), cleaned with AMPure XP beads, checked on an Agilent TapeStation (D1000 High Sensitivity), and sequenced on an Illumina NovaSeq 6000 in 150 bp paired-end mode. Raw FASTQ files were processed through a Snakemake implementation of the Liu et al. (2025) pipeline hosted at `github.com/gp-micro/glori` (repository URL reported only in `mdar`).

For the head-to-head Dorado vs GLORI comparison (Figure 3A), sites were required to meet ≥20-read coverage, method-specific confidence filters (Dorado DRACH: A≥0.8, m6A≥0.98; GLORI: p≤0.05), presence in BOTH DMSO and STM2457 samples, and >10% predicted m6A/A proportion in DMSO. This intersection filter explains why Figure 3B Dorado totals (72,372 NHDF DRACH) are lower than single-sample DMSO counts in Supplementary file 2 (118,374 NHDF DRACH).
