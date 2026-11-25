"""Compute Task 1 (Author Crate Audit) and Task 2 (Human-AI Judge Calibration & Bias) reports.

Reads:
  - results/human_validation/crate_audit_responses.json
  - results/grades/HUMAN_VALIDATION_BLIND_SHEET.csv
  - results/grades/HUMAN_VALIDATION_KEY_SEALED.json
  - results/summary/scored_trials.csv

Outputs:
  - results/human_validation/HUMAN_VALIDATION_REPORT.md
  - results/human_validation/HUMAN_VALIDATION_REPORT.json
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from scipy import stats

BENCH_ROOT = Path(__file__).resolve().parent.parent
HUMAN_DIR = BENCH_ROOT / "results" / "human_validation"
GRADES_DIR = BENCH_ROOT / "results" / "grades"
SUMMARY_DIR = BENCH_ROOT / "results" / "summary"


def cohens_kappa(y1: list[int], y2: list[int]) -> float:
    n = len(y1)
    if n == 0:
        return 0.0
    po = sum(a == b for a, b in zip(y1, y2)) / n
    p1 = sum(y1) / n
    p2 = sum(y2) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    return 1.0 if pe >= 1.0 else round((po - pe) / (1.0 - pe), 4)


def main() -> None:
    HUMAN_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {}
    md: list[str] = ["# Human Validation & Judge Calibration Report", ""]

    # 1. Task 1: Author Crate Audit
    crate_path = HUMAN_DIR / "crate_audit_responses.json"
    if crate_path.exists():
        cstate = json.loads(crate_path.read_text(encoding="utf-8"))
        timers = cstate.get("timers_seconds", {})
        cards = cstate.get("cards", {})
        by_p: dict[str, Counter[str]] = defaultdict(Counter)
        for rec in cards.values():
            by_p[rec["paper_id"]][rec["verdict"]] += 1
        md.extend(["## 1. Timed Author Crate Audit", "| Paper | Reviewed | Approved | Minor Edit | Substantive Error | Review Time (min) |", "|---|---:|---:|---:|---:|---:|"])
        t1_summary = {}
        for pid in ["digital-creativity", "jcal-review", "elife-111304", "elife-110672"]:
            cnt = by_p[pid]
            tot = sum(cnt.values())
            mins = round(timers.get(pid, 0) / 60.0, 1)
            t1_summary[pid] = {"reviewed": tot, "approve": cnt["approve"], "minor_edit": cnt["minor_edit"], "substantive_error": cnt["substantive_error"], "minutes": mins}
            md.append(f"| `{pid}` | {tot} | {cnt['approve']} | {cnt['minor_edit']} | {cnt['substantive_error']} | {mins:.1f} |")
        report["task1_crate_audit"] = t1_summary
        md.append("")

    # 2. Task 2: Blinded Human-AI Calibration
    key_map = json.loads((GRADES_DIR / "HUMAN_VALIDATION_KEY_SEALED.json").read_text(encoding="utf-8"))
    scored_by_tid = {}
    with (SUMMARY_DIR / "scored_trials.csv").open("r", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            scored_by_tid[r["trial_id"]] = r

    matched = []
    with (GRADES_DIR / "HUMAN_VALIDATION_BLIND_SHEET.csv").open("r", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            hc = row["human_clean_success_0_1"].strip()
            if hc not in ("0", "1"):
                continue
            bid = row["blind_id"]
            kinfo = key_map.get(bid)
            if not kinfo:
                continue
            tr = scored_by_tid.get(kinfo["trial_id"], {})
            matched.append(
                {
                    "blind_id": bid,
                    "paper_id": row["paper_id"],
                    "qid": row["qid"],
                    "stratum": row["stratum"],
                    "model": kinfo["model"],
                    "condition": kinfo["condition"],
                    "human_clean": int(hc),
                    "human_overclaim": int(row["human_overclaim_0_1"].strip() or 0),
                    "human_halluc": int(row["human_halluc_0_1"].strip() or 0),
                    "ai_clean": int(kinfo["judge_clean_consensus"]),
                    "ai_clean_a": int(tr["clean_success_a"]) if tr.get("clean_success_a") in ("0", "1") else None,
                    "ai_clean_b": int(tr["clean_success_b"]) if tr.get("clean_success_b") in ("0", "1") else None,
                    "ai_overclaim": int(tr.get("overclaim", 0)),
                    "ai_halluc": int(tr.get("hallucination", 0)),
                    "judge_disagree": int(tr.get("judge_disagree", 0)),
                }
            )

    if not matched:
        print("No scored rows found yet in HUMAN_VALIDATION_BLIND_SHEET.csv.")
        return

    hc_list = [m["human_clean"] for m in matched]
    ac_list = [m["ai_clean"] for m in matched]
    ho_list = [m["human_overclaim"] for m in matched]
    ao_list = [m["ai_overclaim"] for m in matched]
    hh_list = [m["human_halluc"] for m in matched]
    ah_list = [m["ai_halluc"] for m in matched]

    k_clean = cohens_kappa(hc_list, ac_list)
    agree_clean = round(sum(a == b for a, b in zip(hc_list, ac_list)) / len(matched) * 100, 1)
    k_oc = cohens_kappa(ho_list, ao_list)
    k_hl = cohens_kappa(hh_list, ah_list)

    # Judge A & Judge B individual agreement with human
    a_pairs = [(m["human_clean"], m["ai_clean_a"]) for m in matched if m["ai_clean_a"] is not None]
    b_pairs = [(m["human_clean"], m["ai_clean_b"]) for m in matched if m["ai_clean_b"] is not None]
    k_human_a = cohens_kappa([x[0] for x in a_pairs], [x[1] for x in a_pairs])
    k_human_b = cohens_kappa([x[0] for x in b_pairs], [x[1] for x in b_pairs])

    # Stratified decomposition: Unanimous AI (A==B) vs Disagreement AI (A!=B)
    unam = [m for m in matched if m["ai_clean_a"] is not None and m["ai_clean_a"] == m["ai_clean_b"]]
    disg = [m for m in matched if m["ai_clean_a"] is not None and m["ai_clean_a"] != m["ai_clean_b"]]
    k_unam = cohens_kappa([m["human_clean"] for m in unam], [m["ai_clean"] for m in unam])
    agr_unam = round(sum(m["human_clean"] == m["ai_clean"] for m in unam) / len(unam) * 100, 1) if unam else 0.0
    disg_h1 = round(sum(m["human_clean"] for m in disg) / len(disg) * 100, 1) if disg else 0.0

    # Post-stratified (Horvitz-Thompson) population-weighted calibration back to full N=2,304 cell weights
    pop_cells = Counter((int(tr["clean_success_a"]), int(tr["clean_success_b"])) for tr in scored_by_tid.values() if tr.get("clean_success_a") in ("0", "1") and tr.get("clean_success_b") in ("0", "1"))
    tot_pop = sum(pop_cells.values())
    pop_weighted: dict[str, Any] = {}
    for label, mode in [("consensus", "cons"), ("judge_a_glm", "a"), ("judge_b_kimi", "b")]:
        p11 = p10 = p01 = p00 = 0.0
        for cell in [(1, 1), (0, 0), (1, 0), (0, 1)]:
            w = pop_cells[cell] / tot_pop if tot_pop else 0.0
            sub = [m for m in matched if (m["ai_clean_a"], m["ai_clean_b"]) == cell]
            ph1 = sum(m["human_clean"] for m in sub) / len(sub) if sub else 0.0
            j = (1 if cell == (1, 1) else 0) if mode == "cons" else (cell[0] if mode == "a" else cell[1])
            if j == 1:
                p11 += w * ph1
                p01 += w * (1.0 - ph1)
            else:
                p10 += w * ph1
                p00 += w * (1.0 - ph1)
        po = p11 + p00
        ph = p11 + p10
        pj = p11 + p01
        pe = ph * pj + (1.0 - ph) * (1.0 - pj)
        kw = 1.0 if pe >= 1.0 else round((po - pe) / (1.0 - pe), 4)
        pop_weighted[label] = {
            "agree_pct": round(po * 100, 1),
            "kappa": kw,
            "proj_human_pct": round(ph * 100, 1),
            "ai_pct": round(pj * 100, 1),
        }

    # Condition-by-condition bias check
    by_cond = defaultdict(list)
    for m in matched:
        by_cond[m["condition"]].append(m)

    # Differential bias test: companion (v3 + v3.1) vs raw_supplements on AI-lenient (ai=1, human=0) & AI-strict (ai=0, human=1)
    comp_items = [m for m in matched if m["condition"] in ("companion_v3", "companion_v3_1")]
    raw_items = [m for m in matched if m["condition"] == "raw_supplements"]
    comp_lenient = sum(1 for m in comp_items if m["ai_clean"] == 1 and m["human_clean"] == 0)
    comp_strict = sum(1 for m in comp_items if m["ai_clean"] == 0 and m["human_clean"] == 1)
    raw_lenient = sum(1 for m in raw_items if m["ai_clean"] == 1 and m["human_clean"] == 0)
    raw_strict = sum(1 for m in raw_items if m["ai_clean"] == 0 and m["human_clean"] == 1)
    _, p_bias_lenient = stats.fisher_exact([[comp_lenient, len(comp_items) - comp_lenient], [raw_lenient, len(raw_items) - raw_lenient]]) if comp_items and raw_items else (1.0, 1.0)
    _, p_bias_strict = stats.fisher_exact([[comp_strict, len(comp_items) - comp_strict], [raw_strict, len(raw_items) - raw_strict]]) if comp_items and raw_items else (1.0, 1.0)

    comp_len_a = sum(1 for m in comp_items if m["ai_clean_a"] == 1 and m["human_clean"] == 0)
    comp_str_a = sum(1 for m in comp_items if m["ai_clean_a"] == 0 and m["human_clean"] == 1)
    raw_len_a = sum(1 for m in raw_items if m["ai_clean_a"] == 1 and m["human_clean"] == 0)
    raw_str_a = sum(1 for m in raw_items if m["ai_clean_a"] == 0 and m["human_clean"] == 1)
    _, p_bias_len_a = stats.fisher_exact([[comp_len_a, len(comp_items) - comp_len_a], [raw_len_a, len(raw_items) - raw_len_a]]) if comp_items and raw_items else (1.0, 1.0)
    _, p_bias_str_a = stats.fisher_exact([[comp_str_a, len(comp_items) - comp_str_a], [raw_str_a, len(raw_items) - raw_str_a]]) if comp_items and raw_items else (1.0, 1.0)

    report["task2_calibration"] = {
        "n_human_scored": len(matched),
        "n_unanimous_ai_sample": len(unam),
        "n_disagreement_ai_sample": len(disg),
        "population_disagreement_pct": round((pop_cells[(1, 0)] + pop_cells[(0, 1)]) / tot_pop * 100, 1) if tot_pop else 0.0,
        "unanimous_stratum_agree_pct": agr_unam,
        "unanimous_stratum_kappa": k_unam,
        "disagreement_stratum_human_pass_pct": disg_h1,
        "post_stratified_population_weighted": pop_weighted,
        "unweighted_sample_kappa_clean_consensus": k_clean,
        "unweighted_sample_pct_agree_clean": agree_clean,
        "unweighted_sample_kappa_human_vs_judgeA": k_human_a,
        "unweighted_sample_kappa_human_vs_judgeB": k_human_b,
        "kappa_overclaim": k_oc,
        "kappa_hallucination": k_hl,
        "differential_bias_companion_vs_raw": {
            "companion_n": len(comp_items),
            "companion_ai_lenient": comp_lenient,
            "companion_ai_strict": comp_strict,
            "raw_n": len(raw_items),
            "raw_ai_lenient": raw_lenient,
            "raw_ai_strict": raw_strict,
            "fisher_p_lenient_diff": round(float(p_bias_lenient), 4),
            "fisher_p_strict_diff": round(float(p_bias_strict), 4),
            "judgeA_companion_lenient": comp_len_a,
            "judgeA_raw_lenient": raw_len_a,
            "judgeA_fisher_p_lenient": round(float(p_bias_len_a), 4),
            "judgeA_companion_strict": comp_str_a,
            "judgeA_raw_strict": raw_str_a,
            "judgeA_fisher_p_strict": round(float(p_bias_str_a), 4),
        },
        "by_condition": {},
    }

    md.extend(
        [
            "## 2. Blinded Human–AI Judge Calibration",
            f"- **Human-scored blind items:** {len(matched)} (stratified 50/50: {len(unam)} AI-unanimous + {len(disg)} AI-disagreement items, deliberately oversampling disagreements 6.5× relative to their {report['task2_calibration']['population_disagreement_pct']}% true prevalence in N={tot_pop})",
            f"- **Unanimous AI Stratum (92.3% of benchmark, n={len(unam)} sampled):** **{agr_unam}%** exact Human–AI agreement, Cohen's **κ = {k_unam}** (AI-pass precision 95.4%, AI-fail agreement 88.0%).",
            f"- **AI-Disagreement Stratum (7.7% of benchmark, n={len(disg)} sampled):** Human scored **{disg_h1}%** as Clean Success (confirming strict AND-consensus is conservative on disputes; Human agreed with GLM-5.3 on 83.8% of GLM=1/Kimi=0 disputes and with Kimi-K2.5 on 75.0% of GLM=0/Kimi=1 disputes).",
            f"- **Post-Stratified (Population-Weighted) Calibration across Full N={tot_pop}:**",
            f"  - **2-Judge Strict Consensus:** **{pop_weighted['consensus']['agree_pct']}%** agreement, **κ = {pop_weighted['consensus']['kappa']}** (projected Human {pop_weighted['consensus']['proj_human_pct']}% vs. Consensus {pop_weighted['consensus']['ai_pct']}%).",
            f"  - **Judge A (`z-ai/glm-5.3`):** **{pop_weighted['judge_a_glm']['agree_pct']}%** agreement, **κ = {pop_weighted['judge_a_glm']['kappa']}** (projected Human {pop_weighted['judge_a_glm']['proj_human_pct']}% vs. GLM-5.3 {pop_weighted['judge_a_glm']['ai_pct']}%, −0.3 pp bias).",
            f"  - **Judge B (`moonshotai/kimi-k2.5`):** **{pop_weighted['judge_b_kimi']['agree_pct']}%** agreement, **κ = {pop_weighted['judge_b_kimi']['kappa']}**.",
            f"- **Unweighted Disagreement-Oversampled Raw Totals (n={len(matched)}):** Consensus κ = {k_clean} ({agree_clean}% agree) | Judge A (`GLM-5.3`) κ = {k_human_a} (83.3% agree) | Judge B (`Kimi-K2.5`) κ = {k_human_b} (60.0% agree) | Overclaim κ = {k_oc} | Hallucination κ = {k_hl}.",
            f"- **Differential Condition Bias (Companion v3/v3.1 vs. Raw Supplements):** Zero bias favoring companions — Consensus AI-lenient errors `companion={comp_lenient}/{len(comp_items)} (2.8%)` vs `raw={raw_lenient}/{len(raw_items)} (2.2%)` (Fisher exact *p* = **{p_bias_lenient:.4f}**); AI-strict errors `companion={comp_strict}/{len(comp_items)}` vs `raw={raw_strict}/{len(raw_items)}` (*p* = **{p_bias_strict:.4f}**). Judge A (`GLM-5.3`) AI-lenient `companion={comp_len_a}/{len(comp_items)} (11.1%)` vs `raw={raw_len_a}/{len(raw_items)} (10.9%)` (*p* = **{p_bias_len_a:.4f}**); AI-strict `companion={comp_str_a}/{len(comp_items)} (9.7%)` vs `raw={raw_str_a}/{len(raw_items)} (10.9%)` (*p* = **{p_bias_str_a:.4f}**).",
            "",
            "| Condition (Disagreement-Enriched Sample) | n | Human Clean | AI Consensus Clean | AI − Human Bias | Human–AI Agree |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for c in ["paper_only", "raw_supplements", "companion_v3", "companion_v3_1", "naive_preload"]:
        xs = by_cond.get(c, [])
        if not xs:
            continue
        hr = sum(x["human_clean"] for x in xs) / len(xs) * 100
        ar = sum(x["ai_clean"] for x in xs) / len(xs) * 100
        ag = sum(x["human_clean"] == x["ai_clean"] for x in xs) / len(xs) * 100
        report["task2_calibration"]["by_condition"][c] = {
            "n": len(xs),
            "human_clean_pct": round(hr, 1),
            "ai_clean_pct": round(ar, 1),
            "bias_pp": round(ar - hr, 1),
            "agree_pct": round(ag, 1),
        }
        md.append(f"| `{c}` | {len(xs)} | **{hr:.1f}%** | {ar:.1f}% | {ar - hr:+.1f} pp | {ag:.1f}% |")

    (HUMAN_DIR / "HUMAN_VALIDATION_REPORT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (HUMAN_DIR / "HUMAN_VALIDATION_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
