---
id: Q02
title: GLORI conversion bias, unresolved method differences, and Fig 3D directionality
type: qualification
temporal_status: peer_review_revision
source_locators:
- public_reviews:13
- author_response:19-21
- author_response:27-29
- author_response:45-47
- article:240-242
- article:306
- supp3_s1_Sheet1:2-6
relations:
- type: qualifies
  target: C02
  basis: GLORI-only calls are unresolved, not proven false positives
- type: qualifies
  target: C04
  basis: Illustrates long-read capability, not broad superiority
- type: qualifies
  target: M04
  basis: 94.8–95.4% conversion confounds low-stoichiometry GLORI calls
- type: qualifies
  target: D03
  basis: Sub-optimal conversion and <80M reads in HD10.6 GLORI
linked_cards:
- U01
---

# Q02: GLORI conversion bias, unresolved method differences, and Fig 3D directionality

Peer review established three critical caveats governing any comparison between Dorado and GLORI in this study. First, the data do NOT prove that GLORI-only sites are false positives, that GLORI has reduced specificity, or that Dorado serves as a validating reference standard (`author_response:19-21`). In NHDFs, GLORI read-coverage distributions were comparable between shared and GLORI-only sites, and all analyzed sites were STM2457-responsive. However, the study's GLORI libraries achieved only 94.8–95.4% gene-wide A-to-I conversion (`supp3`; >5% non-conversion vs 98–99% in Shen et al., 2024), which disproportionately confounds calls in the 10–20% stoichiometry range where GLORI-only sites cluster. Thus, discordance reflects unresolved method-specific differences and technical conversion limits.

Second, Reviewer #2 highlighted an asymmetry in Figure 3D (`author_response:45-47`): the reported overlap percentages (48.8% at ≥10% up to >93% at ≥80%) are computed with **GLORI sites as the denominator** (13,614 / 27,926 GLORI DRACH sites = 48.75%), showing that Dorado recovers high-proportion GLORI sites. They do NOT show that 48.8% of Dorado calls are validated by GLORI—using Dorado DRACH sites (72,372) as denominator yields 18.8% overlap. Note a residual Discussion error at `article:306`, which still says 'only 50% of m6A sites... identified by Dorado were also present in the GLORI data.'

Third, per `public_reviews:13` and `author_response:27-29`, the four isoform loci illustrate long-read variant assignment rather than proving broad quantitative superiority of Dorado over short-read GLORI.
