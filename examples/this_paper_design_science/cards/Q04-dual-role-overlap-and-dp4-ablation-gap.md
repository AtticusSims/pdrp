---
id: Q04
title: Dual-role reader overlap (Grok 4.6 & DeepSeek V3.2) with exclusion checks,
  and missing direct DP4 ablation
type: qualification
temporal_status: current
source_locators:
- article:143-147
- article:200-201
- article:234-236
- article:313-315
- article:330-337
- supplement_s1:125-143
relations:
- type: qualifies
  target: C04
  basis: Grok 4.6 (question author) and DeepSeek V3.2 (auditor) also ran as stateless
    readers
- type: qualifies
  target: M01
  basis: No main-benchmark arm disabled software co-retrieval over identical cards
    (DP4)
- type: qualifies
  target: C02
  basis: Verifies abstention win strengthens (+14.6 pp) when both dual-role models
    are excluded
linked_cards:
- C04
- M01
- C02
---

# Q04: Dual-role reader overlap (Grok 4.6 & DeepSeek V3.2) with exclusion checks, and missing direct DP4 ablation

Two experimental design qualifications govern attribution of protocol gains (article:145, 200, 235, 313-315, 330-336; supplement_s1:125-143). First, although both blinded judges (GLM-5.3 and Kimi-K2.5) and the companion drafter (Gemini 4 Neon) had zero overlap with any reader model, Grok 4.6 (author of the 64 card-blind questions from raw archives) and DeepSeek V3.2 (adversarial card auditor) also participated as stateless reader subjects. Leave-one-out and leave-both-out sensitivity checks (Table S4, supplement_s1:129-143) confirm that dual roles did NOT inflate protocol gains—excluding them actually strengthened headline results: Frontier-3 excluding Grok 4.6 rose to 93.2% vs. 88.5% raw BM25 (+4.7 pp, +12/-3, p = 0.0352, 0/192 hallucinations), 6-model overall excluding both rose to +3.6 pp (p = 0.0759), and 6-model unanswerable abstention rose to 85.4% vs. 70.8% (+14.6 pp, +7/-0, p = 0.0156). Second, regarding Design Principle 4 (software-enforced caveat co-retrieval), the main benchmark did NOT include an isolated arm turning co-retrieval OFF over identical cards. Randomized 8-model qualification-binding gains vs. strong BM25 were directional (+2.3 pp Cycle 1; +5.5 pp Cycle 2, p = 0.189; results_report:59-82), while strong within-model adherence appeared in Frontier-4 (92.2% vs. 82.8%, 0% overclaims, 63/64 cards opened) and DeepSeek V3.2 (56.2% Cycle 1 vs. 25.0% raw OFF; 50.0% Cycle 2 vs. 18.8% raw ON). DP4's contrast against passive hyperlinks therefore rests on preliminary prototyping plus within-model adherence and randomized gains over full-card preloading.
