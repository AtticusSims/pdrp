---
id: C05
title: Non-DRACH Dorado calls mix basecalling artefacts with plausible writers
type: claim
temporal_status: original_article
source_locators:
- article:236
- article:262-269
- article:278-280
- article:304
- author_response:15-17
relations:
- type: supports
  target: C01
  basis: STM2457 separates METTL3-dependent vs independent calls
- type: uses
  target: M01
  basis: STM2457 perturbation in NHDFs
linked_cards:
- Q01
- Q03
- U01
---

# C05: Non-DRACH Dorado calls mix basecalling artefacts with plausible writers

Even after stringent probability (≥0.98) and proportion (≥10%) filtering, Dorado calls m6A outside the canonical DRACH consensus: >100 non-DRACH motifs appear in NHDF DRACH-model output and >3,000 non-DRACH sites appear in the all-context dissection (note also ~9,000 non-DRACH sites in the Fig 3B comparison between 81,012 all-context and 72,372 DRACH calls). Inspecting the top 15 non-DRACH motifs reveals that technical artefacts and plausible biology coexist.

In the DRACH model, the top four non-DRACH motifs—AAAAC, AAAAA, ACACU, and GGACG—are largely STM2457-sensitive. Two top-15 motifs fit DRAC (non-DRACH) and likely represent authentic methylation, whereas other calls reflect three nanopore/basecalling artefacts: (1) 1–2 nt positional shifts adjacent to true DRACH sites (exemplified by ACACU); (2) heterozygous SNPs making the 5-mer DRACH in half the reads (exemplified by GGACG with 51% G vs 49% A at the terminal position); and (3) homopolymer localization imprecision (AAAAA/AAAAC).

In the all-context model (top four: GGACG, GUACU, AGACG, GGAUU), sites split into STM2457-sensitive and STM2457-insensitive classes. STM2457-sensitive GGAUU shows no positional shift, SNP, or homopolymer artefact and is presented as a plausible METTL3-dependent candidate (supported by in vitro METTL3–METTL14 non-DRACH activity in Zhang et al., DOI: 10.1126/sciadv.ads4750). STM2457-insensitive calls enrich METTL16-like motifs (e.g., ACAGA in MAT2A matching UACAGAGAA), though both classes require orthogonal validation.
