---
id: C03
title: Conserved m6A sites show higher predicted proportions in HD10.6 vs NHDF
type: claim
temporal_status: original_article
source_locators:
- article:251-259
- article:276
- article:282-286
- article:308
- article:392
relations:
- type: uses
  target: M01
  basis: Primary NHDF and differentiated HD10.6 datasets
- type: supports
  target: C01
  basis: Reproducible DRACH and metagene architecture post-filtering
linked_cards:
- Q01
- U01
---

# C03: Conserved m6A sites show higher predicted proportions in HD10.6 vs NHDF

Comparing filtered Dorado v0.9.0 m6A maps across genes expressed in both primary normal human dermal fibroblasts (NHDFs) and terminally differentiated HD10.6 neuron-like cells (~13,000 co-expressed genes) revealed largely conserved site positions alongside a global upward shift in predicted modification proportions in the HD10.6 dataset. Specifically, 87% of HD10.6 high-confidence m6A sites overlapped with NHDFs, yielding n=38,217 shared sites. Site-specific predicted m6A/A proportions correlated strongly across the two datasets (Pearson r=0.93), yet median predicted m6A/A proportion across the 38,217 shared sites rose from 54% in NHDFs to 70.2% in HD10.6 cells.

Both datasets preserved canonical DRACH sequence preferences dominated by GGACU, with higher HD10.6 proportions concentrated in the most abundant DRACH pentamers. Metagene profiling confirmed stop-codon and 3′ UTR enrichment across all poly(A) transcripts, whereas monoexonic transcripts showed broader coding-sequence (CDS) modification; calls below 10% proportion displayed atypical metagene distributions.

DAVID KEGG over-representation analysis of genes containing shared m6A sites (p≤0.05 against the ~13,000 co-expressed gene background) enriched pathways related to neurodegeneration, infection, and intracellular signaling. Representative pathway genes (WNTB5, MAPK1, AKT1, NCK1, NRP1) showed elevated predicted m6A/A proportions in HD10.6 cells, whereas the housekeeping control ACTG1 remained uniform across both datasets.
