---
id: D01
title: Dorado read/alignment statistics, denominators, and data/code accessions
type: data
temporal_status: original_supplement
source_locators:
- supp1_s1_Tabelle1:1-16
- mdar:93-101
- article:51
- article:402-406
relations:
- type: derived_from
  target: M02
  basis: Dorado v0.5.0–v0.9.0 and minimap2 alignment metrics
- type: supports
  target: C01
  basis: Documents sequencing depth across conditions and versions
linked_cards:
- Q01
---

# D01: Dorado read/alignment statistics, denominators, and data/code accessions

Exact nanopore sequencing and alignment statistics reside exclusively in `supp1_s1_Tabelle1`, while repository accessions reside exclusively in `mdar` (the `article.txt` Data Availability block is blank). Raw FASTQ and POD5 datasets are deposited at ENA under `PRJEB101380`; R scripts are at `github.com/DepledgeLab/HOLDEN` and the GLORI Snakemake workflow at `github.com/gp-micro/glori`.

Exact Dorado v0.9.0 read statistics (`m6A_DRACH` and `all mods` identical):
- **NHDF_DMSO:** 13,257,968 total; 1,768,357 unaligned; 11,489,611 HG38+RCS aligned (86.66%); 34,932 RCS (0.30%); 11,454,678 HG38 primary (99.70% of aligned; 86.40% of total); 10,985,331 Gencode47 (82.86%).
- **NHDF_STM2457:** 13,279,548 total; 2,368,236 unaligned; 10,911,312 aligned (82.17%); 119,318 RCS (1.09%); 10,791,993 HG38 primary (98.91% of aligned; 81.27% of total); 10,245,811 Gencode47 (77.15%).
- **HD10_DMSO** (`HD10_6_DMSO_48h_1`): 5,640,472 total; 1,286,994 unaligned; 4,353,478 aligned (77.18%); 49,449 RCS (1.14%); 4,304,028 HG38 primary (98.86% of aligned; 76.31% of total); 3,878,093 Gencode47 (68.75%).
- **HD10_STM2457** (`HD10_6_STM2457_48h_1`): 10,627,755 total; 2,890,301 unaligned; 7,737,454 aligned (72.80%); 95,351 RCS (1.23%); 7,642,102 HG38 primary (98.77% of aligned; 71.91% of total); 6,861,636 Gencode47 (64.56%).

Earlier NHDF_DMSO basecalls yielded 13,006,045 (v0.5.0), 12,936,369 (v0.6.0), 13,281,756 (v0.7.0), and 13,257,968 (v0.8.0) reads. Crucially, the article's '>98% primary alignment to hg38' uses aligned reads (HG38+RCS) as denominator, not total called reads (71.91–86.40%). IVT library read stats are omitted from `supp1`.
