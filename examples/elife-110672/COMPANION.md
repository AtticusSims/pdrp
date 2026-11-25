# Calibrated analysis framework for nanopore direct RNA sequencing uncovers cell-specific m6A proportions at conserved sites

DOI: 10.7554/eLife.110672 | VOR v1: 2026-11-20 | CC-BY-4.0 | 4 reviewed preprints -> VOR

## Coverage Map
- **Only in supp1-supp4:** Dorado read/alignment/RCS stats (supp1); >=20-read filt/unfilt site counts & NHDF IVT (supp2); GLORI reads & 94.8-95.4% CR (supp3); 5-isoform SPEN coverage (supp4).
- **Only in mdar:** ENA PRJEB101380, GitHub (DepledgeLab/HOLDEN, gp-micro/glori), HD10.6 female STR (PMID:41415445), NHDF <50 doublings, blank replicate rows.
- **Only in elife_assessment_and_versions, public_reviews, author_response:** eLife Assessment (solid benchmarking; weaker biology/accuracy), editors (Batista/Dalal), R1/R2 critiques & revisions.
- **Absent:** Raw POD5/FAST5/FASTQ/BAM, scripts, site/KEGG/viability tables, IVT read stats (supp1), HD10.6/Gencode47 IVT (supp2), biological replicates, wet-lab non-DRACH/pseU/I/m5C validation, IVT primers, preprint dates.

## Card Index
- C01 (claim): IVT-calibrated m6A filters [IVT, STM2457, 0.98, RCS]
- C02 (claim): Dorado recovers high-m6A GLORI [GLORI, 48.8%, DRACH]
- C03 (claim): Higher HD10.6 vs NHDF m6A/A [38217, 70.2%, KEGG]
- C04 (claim): DRS resolves isoform m6A [SPEN, KRTAP1-5, HSPA8, CITED2]
- C05 (claim): Non-DRACH artefacts & writers [GGAUU, ACAGA, MAT2A, SNP]
- M01 (method): Cells, STM2457 & RNA [NHDF, HD10.6, CellTiter-Glo]
- M02 (method): Dorado models, align & Modkit [v0.5-0.9, minimap2, v5.1.0]
- M03 (method): PELT cutoff & subsampling [PELT, log2, 0.585, BBMap]
- M04 (method): GLORI chemistry & filters [NaNO2, UMI, Snakemake]
- D01 (data): Dorado read stats & repos [supp1, PRJEB101380, HOLDEN]
- D02 (data): Site counts by mod/ver/IVT [supp2, pseU, I, m5C]
- D03 (data): GLORI CR & SPEN isoforms [supp3, supp4, CR, ENST]
- Q01 (qualification): No biological replicates [replicates, eLife, MDAR]
- Q02 (qualification): GLORI bias & Fig 3D [non-conversion, 18.8%, GLORI-only]
- Q03 (qualification): pseU/I/m5C errors & cross-react [m5C, C/G, m1psi]
- Q04 (qualification): Cutoff limits & VOR typos [unbiased, FPR, log2]
- U01 (review_disposition): Review claim edits [VOR, Batista, S21, ads4750]
- U02 (update): VOR method/term upgrades [PELT, proportion, background]
