---
id: C04
title: Long-read DRS resolves isoform-specific m6A profiles missed by GLORI
type: claim
temporal_status: original_article
source_locators:
- article:222-224
- article:232-234
- article:245-248
- article:296
- supp4_s1_Dorado_SPEN_isoforms:1-7
relations:
- type: uses
  target: M02
  basis: GENCODE v47 transcriptome alignment with minimap2
- type: derived_from
  target: D03
  basis: SPEN isoform coverage counts in supp4
linked_cards:
- Q01
- Q02
- U01
---

# C04: Long-read DRS resolves isoform-specific m6A profiles missed by GLORI

Aligning Dorado-basecalled DRS reads to the GENCODE v47 human transcriptome yields comparable total m6A site counts to genome alignment while enabling variant-specific m6A assignment that short-read GLORI cannot readily resolve. At the heavily methylated SPEN locus (ENSG00000065526.13, previously reported to carry >100 m6A sites), genome-aligned DRS detected 42 m6A sites compared with only 5 by GLORI. At the transcriptome level (≥20-read coverage cutoff), two of SPEN's seven annotated isoforms were detectable in NHDFs (SPEN-201 at 108 reads and SPEN-202 at 90 reads; three other listed isoforms had 0–5 reads). SPEN-201 harbored more m6A sites with a lower median predicted proportion than SPEN-202.

Three supplementary NHDF loci illustrate distinct scenarios for DRS variant resolution using the DRACH model: (1) monoexonic KRTAP1-5 (single detectable isoform), where DRS identifies more sites than GLORI, especially at lower predicted m6A/A proportions; (2) HSPA8 (five detectable m6A-containing isoforms), where DRS resolves isoform-specific m6A sites across HSPA8-201 and HSPA8-202 unassignable by GLORI; and (3) CITED2 (three detectable m6A-containing isoforms), which exhibits distinct isoform-level modification profiles. Following peer review, these loci are framed as illustrative examples of long-read variant assignment rather than proof that Dorado broadly outperforms GLORI.
