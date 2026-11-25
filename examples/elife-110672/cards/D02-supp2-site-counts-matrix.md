---
id: D02
title: Filtered vs unfiltered site counts across samples, versions, mods, and IVT
type: data
temporal_status: original_supplement
source_locators:
- supp2_s1_Sheet1:1-58
- article:189-195
relations:
- type: derived_from
  target: M02
  basis: Modkit pileup ≥20-read bedMethyl summaries
- type: supports
  target: C01
  basis: Quantifies filtering impact and STM2457 depletion
linked_cards:
- Q03
- Q04
---

# D02: Filtered vs unfiltered site counts across samples, versions, mods, and IVT

`supp2_s1_Sheet1` provides the only complete table of ≥20-read modification site counts (Filtered vs Unfiltered) across Dorado v0.9.0 samples, references (HG38, Gencode47), NHDF IVT controls, and Dorado v0.5.0–v0.9.0 versions. For Dorado v0.9.0 at ≥10% predicted proportion (Filtered [Unfiltered]):
- **NHDF HG38 (DMSO -> STM2457):** m6A(all) 134,701 [444,645] -> 15,545 [293,355]; m6A(DRACH) 118,374 [131,652] -> 10,997 [15,185]; pseU 11,492 [468,616] -> 11,661 [468,982]; I 9,722 [116,548] -> 14,263 [119,832]; m5C 6,930 [253,718] -> 2,130 [203,058].
- **NHDF Gencode47 (DMSO -> STM2457):** m6A(all) 164,265 -> 17,963; m6A(DRACH) 145,548 -> 13,760; pseU 12,953 -> 13,270; I 7,828 -> 11,809; m5C 7,544 -> 2,522.
- **HD10.6 HG38 (DMSO -> STM2457):** m6A(all) 125,316 -> 18,629; m6A(DRACH) 106,755 -> 12,893; pseU 7,035 -> 10,397; I 5,614 -> 14,288; m5C 4,926 -> 1,708 (Gencode47: m6A all 128,959->19,119; DRACH 112,292->14,924; I 3,897->8,049; m5C 4,475->1,773).
- **IVT NHDF HG38 (≥10%):** m6A(all) 264 [14,145]; m6A(DRACH) 3 [93]; pseU 159 [14,315]; I 150 [9,244]; m5C 10 [4,223] (all-stoichiometry unfiltered IVT: 163,150 m6A all; 9,335 DRACH; 143,220 pseU; 84,547 I; 99,715 m5C).
- **Dorado versions (NHDF HG38 ≥10%):** m6A(all) v0.7.0=144,043 [771,772] vs v0.8.0=134,698 / v0.9.0=134,701; m6A(DRACH) v0.5.0=116,673, v0.6.0=116,054, v0.8.0=117,163, v0.9.0=118,374; pseU v0.7.0=9,477 vs v0.8.0/0.9.0=11,492; I and m5C are identical/near-identical between v0.8.0 and v0.9.0. HD10.6 and Gencode47 IVT counts are not reported.
