---
id: Q01
title: Absence of biological replicates and unvalidated biological/isoform claims
type: qualification
temporal_status: peer_review_revision
source_locators:
- elife_assessment_and_versions:10-11
- author_response:31-33
- author_response:41-43
- mdar:67-76
- supp1_s1_Tabelle1:13-16
relations:
- type: qualifies
  target: C03
  basis: No independent biological replicates for NHDF vs HD10.6
- type: qualifies
  target: C04
  basis: Isoform differences lack biological replication and validation
- type: qualifies
  target: C05
  basis: GGAUU and METTL16 candidates lack orthogonal validation
- type: qualifies
  target: D01
  basis: Single sequencing library per condition; unequal HD10.6 depth
linked_cards:
- U01
---

# Q01: Absence of biological replicates and unvalidated biological/isoform claims

The eLife Assessment classifies the technical benchmarking evidence as 'solid' but explicitly flags that 'claims regarding relative method accuracy and cell-type- and isoform-specific biological differences remain less well supported due to limited biological replication and validation.' Reviewer #2 specifically identified that the NHDF vs HD10.6 sequencing comparison lacks independent biological replicates.

Multiple corpus records corroborate this design limitation: in the MDAR checklist (`mdar:75-76`), both rows asking for laboratory replication counts and biological vs technical replicate definitions are left completely blank (while sample-size determination, randomization, blinding, and attrition are marked N/A); `supp1_s1_Tabelle1` lists single sequencing libraries per condition (e.g., `HD10_6_DMSO_48h_1`, `HD10_6_STM2457_48h_1`) with nearly 2× depth imbalance between HD10.6 DMSO (5.64M reads) and STM2457 (10.63M reads). The only replicated measurements reported are 10 CellTiter-Glo viability wells per condition and 10 computational 200,000-read BAM subsampling seeds.

Consequently, the 70.2% vs 54% median m6A/A shift should be interpreted as a difference between two individual fibroblast and neuronal datasets rather than a proven general cell-type rule (note the authors revised the Abstract and Results headings accordingly but retained 'cell-specific' in the paper title). Functional impacts on RNA stability, translation, or neuronal physiology remain untested hypotheses, and non-DRACH `GGAUU` and putative METTL16 `ACAGA` sites lack orthogonal or knockdown validation.
