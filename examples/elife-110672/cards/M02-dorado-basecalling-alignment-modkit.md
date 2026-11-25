---
id: M02
title: Dorado SQK-RNA004 basecalling, Remora models, alignment, and Modkit pileup
type: method
temporal_status: original_article
source_locators:
- article:37
- article:213
- article:351-366
- article:375-380
- supp1_s1_Tabelle1:2-16
relations:
- type: uses
  target: M01
  basis: Processes poly(A) RNA and IVT libraries
- type: supports
  target: D01
  basis: Generates BAM/FASTQ and alignment counts
- type: supports
  target: D02
  basis: Generates filtered and unfiltered Modkit site tables
linked_cards:
- Q03
- Q04
- U02
---

# M02: Dorado SQK-RNA004 basecalling, Remora models, alignment, and Modkit pileup

Direct RNA sequencing used 250–300 ng isolated poly(A) RNA plus 25 ng Enolase II RNA calibration strand (RCS) with ONT SQK-RNA004 chemistry on individual PromethION RNA flow cells (PromethION 2 Solo, 48 hr). Basecalling ran in super-accuracy mode with adapter trimming across five Dorado releases and three Remora model generations: m6A DRACH in v0.5.0/v0.6.0 (`rna004_130bps_sup@v3.0.1_m6A_DRACH@v1`) and v0.8.0/v0.9.0 (`rna004_130bps_sup@v5.1.0`); all-context m6A in v0.7.0 (`rna004_130bps_sup@v5.0.0_m6A@v1`) and v0.8.0/v0.9.0 (`v5.1.0`); Ψ in v0.7.0 (`v5.0.0_pseU@v1`) and v0.8.0/v0.9.0 (`v5.1.0`); and inosine/m5C with `v5.1.0` (Methods cites v0.9.0; `supp1`/`supp2` also include v0.8.0 all-mods outputs).

Unaligned BAMs were converted to tag-preserving FASTQ via SAMtools v1.18 (`samtools fastq -TMM,ML`). Minimap2 v2.26 aligned reads to (a) combined GRCh38.p14 + RCS (`-ax splice -k14 -y -uf --secondary=no`, primary filter `samtools view -b -F2308`) and (b) GENCODE v47 transcriptome (`map-ont`, `-t 8 -y -L -p 0.99`, primary filter `-F2324`), then sorted and indexed.

Modkit v0.4.1 `sample-probs` (`--hist --only-mapped --percentiles 0.1..0.9` incl. `0.85`, `-f 0.1`; RCS `-f 0.25`) extracted probability histograms. Modkit `pileup` applied canonical base filters (`--filter-threshold A/T/C/G:0.8`), reference-base `--motif` matching, and modification thresholds (`--mod-thresholds a:0.98` for m6A; `0.99` for Ψ, inosine, and m5C) to produce filtered vs unfiltered bedMethyl outputs, subsequently requiring ≥20 valid reads per site.
