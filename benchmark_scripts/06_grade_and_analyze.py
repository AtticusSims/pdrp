"""Blinded cross-family 2-judge grading, statistical analysis, and Human Validation Packet exporter.

Evaluates every answer against the question's atomic binary rubric items plus three explicit error flags:
  - hallucination_or_invention
  - overclaim_or_dropped_qualification
  - false_absence_or_wrong_abstention

Computes:
  - Inter-judge Cohen's kappa
  - Paired McNemar exact tests & Wilcoxon signed-rank tests (companion_v3 vs raw_supplements, paper_only, naive_preload)
  - 1,000-resample bootstrap 95% confidence intervals
  - Token & latency efficiency tables
  - Stratified 20% blinded Human Validation Audit Packet (CSV + Markdown)
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import random
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from openrouter_client import get_ollama_client, get_openrouter_client

BENCH_ROOT = Path(__file__).resolve().parent.parent
BENCHMARK_DIR = BENCH_ROOT / "benchmark"
RESULTS_RAW_DIR = BENCH_ROOT / "results" / "raw"
GRADES_DIR = BENCH_ROOT / "results" / "grades"
SUMMARY_DIR = BENCH_ROOT / "results" / "summary"

JUDGE_SYSTEM = """You are a strict, fair, blinded scientific answer grader.
You evaluate an AI assistant's answer against a fixed atomic rubric and verbatim source anchors.
You do NOT know which model or condition produced the answer.

Grading rules:
1. Score each atomic rubric item independently as 1 (clearly satisfied, accepting equivalent wording and source-consistent rounding) or 0 (missing, contradicted, or distorted).
2. Do NOT penalize benign everyday phrasing (e.g., ordinary prose synonyms) when the quantitative and methodological facts are accurate.
3. Set `hallucination_or_invention` = true ONLY if the answer states a fabricated number, nonexistent table/analysis, or false factual assertion contradicted by the anchors.
4. Set `overclaim_or_dropped_qualification` = true if the answer makes an unwarranted causal/generalization claim, conflates populations/denominators/versions, or asserts a headline finding while dropping a critical limitation or negative control specified in the rubric or error traps.
5. Set `false_absence_or_wrong_abstention` = true if (a) for an answerable question, the answer falsely claims the information is absent/unreported, OR (b) for an `unanswerable: true` question, the answer fails to abstain and fabricates a concrete answer.
6. Set `grounded_citation` = true if the answer cites at least one specific verifiable location (section, table, card ID, or source_id/line).

Return ONLY a valid JSON object:
{
  "item_scores": {"u1": 1, "u2": 0, ...},
  "hallucination_or_invention": false,
  "overclaim_or_dropped_qualification": false,
  "false_absence_or_wrong_abstention": false,
  "grounded_citation": true,
  "brief_rationale": "1-2 concise sentences explaining any 0 score or true error flag."
}"""


def opaque_trial_id(rec: dict[str, Any]) -> str:
    raw = f"{rec['qid']}|{rec['model']}|{rec['condition']}|{rec.get('completed_utc', '')}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_all_trials() -> list[dict[str, Any]]:
    # Deduplicate by (model, condition, qid), keeping the latest valid completed answer
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for p in sorted(RESULTS_RAW_DIR.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            key = (rec["model"], rec["condition"], rec["qid"])
            prev = by_key.get(key)
            if prev is None or (rec.get("final_answer") and not rec.get("error")):
                by_key[key] = rec
    trials = list(by_key.values())
    for t in trials:
        t["trial_id"] = opaque_trial_id(t)
    return trials


def extract_json_object(raw: str) -> dict[str, Any]:
    s = (raw or "").strip()
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.S).strip()
    try:
        return json.loads(s)
    except Exception:
        start = s.find("{")
        end = s.rfind("}")
        if start >= 0 and end > start:
            return json.loads(s[start : end + 1])
        raise ValueError(f"No valid JSON object found in judge output ({len(s)} chars): {s[:160]!r}")


async def grade_with_judge(
    judge_name: str,
    provider: str,
    model_id: str,
    trials: list[dict[str, Any]],
    qmap: dict[str, dict[str, Any]],
    concurrency: int = 8,
) -> dict[str, dict[str, Any]]:
    GRADES_DIR.mkdir(parents=True, exist_ok=True)
    out_path = GRADES_DIR / f"judge_{judge_name}.jsonl"
    existing: dict[str, dict[str, Any]] = {}
    if out_path.exists():
        for line in out_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                g = json.loads(line)
                if "item_scores" in g:
                    existing[g["trial_id"]] = g
            except Exception:
                pass

    todo = [t for t in trials if t["trial_id"] not in existing]
    if not todo:
        print(f"  [DONE] Judge {judge_name} ({model_id}): all {len(existing)} graded.", flush=True)
        return existing

    print(f"  [GRADE] Judge {judge_name} ({model_id}, {provider}): {len(todo)} pending...", flush=True)
    client = (
        get_openrouter_client(async_mode=True, timeout=180.0)
        if provider == "openrouter"
        else get_ollama_client(async_mode=True, timeout=240.0)
    )
    sem = asyncio.Semaphore(concurrency if provider == "openrouter" else 1)
    lock = asyncio.Lock()
    done_now = 0
    err_now = 0

    async def worker(t: dict[str, Any]) -> None:
        nonlocal done_now, err_now
        q = qmap[t["qid"]]
        rubric_ids = [u["id"] for u in q["rubric_items"]]
        if not t.get("final_answer") or t.get("error"):
            grade = {
                "trial_id": t["trial_id"],
                "judge": judge_name,
                "judge_model": model_id,
                "item_scores": {uid: 0 for uid in rubric_ids},
                "hallucination_or_invention": False,
                "overclaim_or_dropped_qualification": False,
                "false_absence_or_wrong_abstention": True,
                "grounded_citation": False,
                "brief_rationale": f"Empty/errored response: {t.get('error')}",
            }
        else:
            user_msg = (
                f"QUESTION ({q['stratum']}, unanswerable={q.get('unanswerable', False)}):\n{q['question']}\n\n"
                f"ATOMIC RUBRIC ITEMS:\n{json.dumps(q['rubric_items'], indent=2)}\n\n"
                f"COMMON ERROR TRAPS:\n{json.dumps(q.get('common_error_traps', []), indent=2)}\n\n"
                f"BLINDED ASSISTANT ANSWER (trial_id={t['trial_id']}):\n{t['final_answer']}\n\n"
                "Return ONLY the raw JSON grading object."
            )
            grade = None
            last_err = ""
            async with sem:
                for attempt in range(1, 4):
                    kwargs: dict[str, Any] = {
                        "model": model_id,
                        "temperature": 0.0,
                        "max_tokens": 3000,
                        "messages": [
                            {"role": "system", "content": JUDGE_SYSTEM},
                            {"role": "user", "content": user_msg},
                        ],
                    }
                    if provider == "openrouter":
                        kwargs["extra_body"] = {"reasoning": {"effort": "low"}}
                    elif provider == "ollama":
                        kwargs["extra_body"] = {"options": {"num_ctx": 16384, "temperature": 0.0, "seed": 20261121}}
                    try:
                        resp = await client.chat.completions.create(**kwargs)
                        raw = resp.choices[0].message.content or ""
                        parsed = extract_json_object(raw)
                        item_scores = {uid: int(bool(parsed.get("item_scores", {}).get(uid, 0))) for uid in rubric_ids}
                        grade = {
                            "trial_id": t["trial_id"],
                            "judge": judge_name,
                            "judge_model": model_id,
                            "item_scores": item_scores,
                            "hallucination_or_invention": bool(parsed.get("hallucination_or_invention", False)),
                            "overclaim_or_dropped_qualification": bool(parsed.get("overclaim_or_dropped_qualification", False)),
                            "false_absence_or_wrong_abstention": bool(parsed.get("false_absence_or_wrong_abstention", False)),
                            "grounded_citation": bool(parsed.get("grounded_citation", False)),
                            "brief_rationale": str(parsed.get("brief_rationale", ""))[:400],
                        }
                        break
                    except Exception as e:
                        last_err = f"attempt {attempt}: {type(e).__name__}: {str(e)[:260]}"
                        await asyncio.sleep(1.5 * attempt)
            if grade is None:
                grade = {"trial_id": t["trial_id"], "judge": judge_name, "error": last_err}

        async with lock:
            with out_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(grade, ensure_ascii=False) + "\n")
            if "item_scores" in grade:
                existing[t["trial_id"]] = grade
            else:
                err_now += 1
            done_now += 1
            if done_now % 25 == 0 or done_now == len(todo):
                print(f"    Judge {judge_name}: {done_now}/{len(todo)} (errs={err_now})", flush=True)

    await asyncio.gather(*(worker(t) for t in todo))
    return existing


def score_metrics(g: dict[str, Any]) -> dict[str, Any]:
    vals = list(g["item_scores"].values())
    frac = (sum(vals) / len(vals)) if vals else 0.0
    all_met = all(v == 1 for v in vals) and len(vals) > 0
    clean = (
        all_met
        and not g["hallucination_or_invention"]
        and not g["overclaim_or_dropped_qualification"]
        and not g["false_absence_or_wrong_abstention"]
    )
    return {
        "rubric_fraction": frac,
        "all_met": all_met,
        "clean_success": clean,
        "hallucination": g["hallucination_or_invention"],
        "overclaim": g["overclaim_or_dropped_qualification"],
        "wrong_abstention": g["false_absence_or_wrong_abstention"],
        "grounded_citation": g["grounded_citation"],
    }


def cohens_kappa(y1: list[int], y2: list[int]) -> float:
    n = len(y1)
    if n == 0:
        return 0.0
    po = sum(a == b for a, b in zip(y1, y2)) / n
    p1 = sum(y1) / n
    p2 = sum(y2) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    return 1.0 if pe >= 1.0 else round((po - pe) / (1.0 - pe), 4)


def mcnemar_exact(a: list[int], b: list[int]) -> dict[str, Any]:
    """Compare binary outcomes a (treatment) vs b (control) on matched items."""
    n10 = sum(x == 1 and y == 0 for x, y in zip(a, b))  # gains
    n01 = sum(x == 0 and y == 1 for x, y in zip(a, b))  # losses
    n_disc = n10 + n01
    pval = float(stats.binomtest(min(n10, n01), n_disc, 0.5).pvalue) if n_disc > 0 else 1.0
    return {
        "n_pairs": len(a),
        "rate_a": round(sum(a) / len(a), 4) if a else 0.0,
        "rate_b": round(sum(b) / len(b), 4) if b else 0.0,
        "delta": round((sum(a) - sum(b)) / len(a), 4) if a else 0.0,
        "gains": n10,
        "losses": n01,
        "ties": len(a) - n_disc,
        "p_mcnemar_exact": round(pval, 6),
    }


def bootstrap_ci(vals: list[float], n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    if not vals:
        return (0.0, 0.0)
    rng = np.random.default_rng(seed)
    arr = np.array(vals, dtype=float)
    means = rng.choice(arr, size=(n_boot, len(arr)), replace=True).mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return (round(float(lo), 4), round(float(hi), 4))


def analyze_and_export(trials: list[dict[str, Any]], gA: dict[str, dict[str, Any]], gB: dict[str, dict[str, Any]], qmap: dict[str, dict[str, Any]]) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)

    # Combine Judge A & Judge B conservatively (mean rubric fraction; consensus clean_success + track disagreements)
    rows: list[dict[str, Any]] = []
    k_clean_a, k_clean_b = [], []
    k_item_a, k_item_b = [], []
    for t in trials:
        tid = t["trial_id"]
        a = gA.get(tid)
        b = gB.get(tid)
        if not a and not b:
            continue
        ma = score_metrics(a) if a else None
        mb = score_metrics(b) if b else None
        if ma and mb:
            k_clean_a.append(int(ma["clean_success"]))
            k_clean_b.append(int(mb["clean_success"]))
            for uid in a["item_scores"]:
                if uid in b["item_scores"]:
                    k_item_a.append(a["item_scores"][uid])
                    k_item_b.append(b["item_scores"][uid])
            rubric_frac = round((ma["rubric_fraction"] + mb["rubric_fraction"]) / 2.0, 4)
            clean = int(ma["clean_success"] and mb["clean_success"])  # strict consensus
            clean_any = int(ma["clean_success"] or mb["clean_success"])
            disagree = int(ma["clean_success"] != mb["clean_success"])
            halluc = int(ma["hallucination"] or mb["hallucination"])
            overclaim = int(ma["overclaim"] or mb["overclaim"])
            wrong_abs = int(ma["wrong_abstention"] or mb["wrong_abstention"])
            cite = int(ma["grounded_citation"] and mb["grounded_citation"])
        else:
            m = ma or mb
            rubric_frac = round(m["rubric_fraction"], 4)
            clean = int(m["clean_success"])
            clean_any = clean
            disagree = 0
            halluc = int(m["hallucination"])
            overclaim = int(m["overclaim"])
            wrong_abs = int(m["wrong_abstention"])
            cite = int(m["grounded_citation"])

        rows.append(
            {
                **{k: t[k] for k in ["trial_id", "qid", "paper_id", "stratum", "sub_type", "unanswerable", "provider", "model", "condition", "latency_seconds", "turns", "tool_call_count", "prompt_tokens", "completion_tokens", "total_tokens", "estimated_cost_usd"]},
                "rubric_fraction": rubric_frac,
                "clean_success": clean,
                "clean_success_a": int(ma["clean_success"]) if ma else None,
                "clean_success_b": int(mb["clean_success"]) if mb else None,
                "judge_disagree": disagree,
                "hallucination": halluc,
                "overclaim": overclaim,
                "wrong_abstention": wrong_abs,
                "grounded_citation": cite,
                "card_calls": sum(1 for tc in t.get("tool_trace", []) if tc["name"] == "read_card"),
                "co_retrieved_total": sum(len(tc.get("co_retrieved_cards", [])) for tc in t.get("tool_trace", [])),
                "search_no_hits": sum(1 for tc in t.get("tool_trace", []) if tc.get("no_hit")),
            }
        )

    # Save master scored CSV
    csv_path = SUMMARY_DIR / "scored_trials.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # Compute summary stats
    kappa_clean = cohens_kappa(k_clean_a, k_clean_b)
    kappa_item = cohens_kappa(k_item_a, k_item_b)

    by_cond = defaultdict(list)
    by_cond_stratum = defaultdict(list)
    by_model_cond = defaultdict(list)
    by_paper_cond = defaultdict(list)
    indexed: dict[tuple[str, str, str], dict[str, Any]] = {}

    for r in rows:
        by_cond[r["condition"]].append(r)
        by_cond_stratum[(r["condition"], r["stratum"])].append(r)
        by_model_cond[(r["model"], r["condition"])].append(r)
        by_paper_cond[(r["paper_id"], r["condition"])].append(r)
        indexed[(r["model"], r["qid"], r["condition"])] = r

    def agg(rs: list[dict[str, Any]]) -> dict[str, Any]:
        if not rs:
            return {}
        n = len(rs)
        return {
            "n": n,
            "clean_rate": round(sum(r["clean_success"] for r in rs) / n, 4),
            "clean_ci95": bootstrap_ci([r["clean_success"] for r in rs]),
            "rubric_mean": round(sum(r["rubric_fraction"] for r in rs) / n, 4),
            "halluc_rate": round(sum(r["hallucination"] for r in rs) / n, 4),
            "overclaim_rate": round(sum(r["overclaim"] for r in rs) / n, 4),
            "wrong_abs_rate": round(sum(r["wrong_abstention"] for r in rs) / n, 4),
            "median_tokens": int(np.median([r["total_tokens"] for r in rs])),
            "median_latency_s": round(float(np.median([r["latency_seconds"] for r in rs])), 2),
            "mean_tool_calls": round(sum(r["tool_call_count"] for r in rs) / n, 2),
            "mean_card_calls": round(sum(r["card_calls"] for r in rs) / n, 2),
            "mean_co_retrieved": round(sum(r["co_retrieved_total"] for r in rs) / n, 2),
        }

    # Paired contrasts
    contrasts = {}
    for c_a, c_b in [
        ("companion_v3_1", "raw_supplements"),
        ("companion_v3_1", "companion_v3"),
        ("companion_v3_1", "paper_only"),
        ("companion_v3_1", "naive_preload"),
        ("companion_v3", "raw_supplements"),
        ("companion_v3", "paper_only"),
        ("companion_v3", "naive_preload"),
        ("raw_supplements", "paper_only"),
    ]:
        # Overall & per-stratum paired comparisons
        for label, filt in [
            ("ALL", lambda r: True),
            ("A:article_only", lambda r: r["stratum"] == "article_only"),
            ("B:supplementary_fact", lambda r: r["stratum"] == "supplementary_fact"),
            ("C:qualification_binding", lambda r: r["stratum"] == "qualification_binding"),
            ("D:temporal_and_abstention", lambda r: r["stratum"] == "temporal_and_abstention"),
        ]:
            a_bin, b_bin, a_frac, b_frac, a_tok, b_tok = [], [], [], [], [], []
            for (m, qid, c), r_a in indexed.items():
                if c != c_a or not filt(r_a):
                    continue
                r_b = indexed.get((m, qid, c_b))
                if not r_b:
                    continue
                a_bin.append(r_a["clean_success"])
                b_bin.append(r_b["clean_success"])
                a_frac.append(r_a["rubric_fraction"])
                b_frac.append(r_b["rubric_fraction"])
                a_tok.append(r_a["total_tokens"])
                b_tok.append(r_b["total_tokens"])
            if not a_bin:
                continue
            mc = mcnemar_exact(a_bin, b_bin)
            diff_f = np.array(a_frac) - np.array(b_frac)
            try:
                p_wilc = float(stats.wilcoxon(diff_f).pvalue) if np.any(diff_f != 0) else 1.0
            except Exception:
                p_wilc = 1.0
            mc["rubric_mean_a"] = round(float(np.mean(a_frac)), 4)
            mc["rubric_mean_b"] = round(float(np.mean(b_frac)), 4)
            mc["rubric_delta"] = round(float(np.mean(diff_f)), 4)
            mc["p_wilcoxon_rubric"] = round(p_wilc, 6)
            mc["median_tok_a"] = int(np.median(a_tok))
            mc["median_tok_b"] = int(np.median(b_tok))
            contrasts[f"{c_a}__vs__{c_b}__{label}"] = mc

    report_obj = {
        "total_scored_trials": len(rows),
        "inter_judge_kappa_clean": kappa_clean,
        "inter_judge_kappa_item": kappa_item,
        "by_condition": {c: agg(rs) for c, rs in sorted(by_cond.items())},
        "by_condition_stratum": {f"{c}|{s}": agg(rs) for (c, s), rs in sorted(by_cond_stratum.items())},
        "by_model_condition": {f"{m}|{c}": agg(rs) for (m, c), rs in sorted(by_model_cond.items())},
        "by_paper_condition": {f"{p}|{c}": agg(rs) for (p, c), rs in sorted(by_paper_cond.items())},
        "paired_contrasts": contrasts,
    }
    (SUMMARY_DIR / "RESULTS_SUMMARY.json").write_text(json.dumps(report_obj, indent=2), encoding="utf-8")

    # Render concise Markdown report
    md = [
        "# Companion v3 Multi-Paper Benchmark — Statistical Results",
        "",
        f"- **Total scored trials:** {len(rows)}",
        f"- **Inter-judge agreement:** Clean-success Cohen's κ = **{kappa_clean}** | Atomic item-level κ = **{kappa_item}**",
        "",
        "## Overall by Condition",
        "| Condition | n | Clean Success (95% CI) | Mean Rubric | Overclaim | Halluc. | Median Tokens | Mean Tool Calls | Mean Card Calls |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for c in ["paper_only", "raw_supplements", "companion_v3", "companion_v3_1", "naive_preload"]:
        if c not in report_obj["by_condition"]:
            continue
        s = report_obj["by_condition"][c]
        md.append(
            f"| `{c}` | {s['n']} | **{s['clean_rate']*100:.1f}%** ({s['clean_ci95'][0]*100:.1f}–{s['clean_ci95'][1]*100:.1f}%) "
            f"| {s['rubric_mean']*100:.1f}% | {s['overclaim_rate']*100:.1f}% | {s['halluc_rate']*100:.1f}% "
            f"| {s['median_tokens']:,} | {s['mean_tool_calls']} | {s['mean_card_calls']} |"
        )
    md.extend(["", "## Key Paired Contrasts (Matched Model × Question)", "| Contrast & Stratum | Pairs | Rate A vs Rate B (Δ) | Gains/Losses | McNemar p | Rubric Δ (Wilcoxon p) | Med. Tokens A vs B |", "|---|---:|---:|---:|---:|---:|---:|"])
    for k, v in sorted(contrasts.items()):
        md.append(
            f"| `{k}` | {v['n_pairs']} | {v['rate_a']*100:.1f}% vs {v['rate_b']*100:.1f}% (**{v['delta']*100:+.1f} pp**) "
            f"| +{v['gains']} / -{v['losses']} | {v['p_mcnemar_exact']:.4g} | {v['rubric_delta']*100:+.1f} pp ({v['p_wilcoxon_rubric']:.4g}) "
            f"| {v['median_tok_a']:,} vs {v['median_tok_b']:,} |"
        )

    md.extend(["", "## Condition × Stratum Breakdown", "| Condition | Stratum | n | Clean Success | Mean Rubric | Overclaim | Halluc. | Wrong Abst. | Med. Tokens |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    for c in ["paper_only", "raw_supplements", "companion_v3", "companion_v3_1", "naive_preload"]:
        for st in ["article_only", "supplementary_fact", "qualification_binding", "temporal_and_abstention"]:
            k = f"{c}|{st}"
            if k not in report_obj["by_condition_stratum"]:
                continue
            s = report_obj["by_condition_stratum"][k]
            md.append(
                f"| `{c}` | `{st}` | {s['n']} | **{s['clean_rate']*100:.1f}%** | {s['rubric_mean']*100:.1f}% "
                f"| {s['overclaim_rate']*100:.1f}% | {s['halluc_rate']*100:.1f}% | {s['wrong_abs_rate']*100:.1f}% | {s['median_tokens']:,} |"
            )

    md.extend(["", "## Model × Condition Breakdown", "| Model | Condition | n | Clean Success | Mean Rubric | Overclaim | Med. Tokens | Med. Latency (s) | Mean Tools |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"])
    models_seen = sorted({r["model"] for r in rows})
    for m in models_seen:
        for c in ["paper_only", "raw_supplements", "companion_v3", "companion_v3_1", "naive_preload"]:
            k = f"{m}|{c}"
            if k not in report_obj["by_model_condition"]:
                continue
            s = report_obj["by_model_condition"][k]
            md.append(
                f"| `{m}` | `{c}` | {s['n']} | **{s['clean_rate']*100:.1f}%** | {s['rubric_mean']*100:.1f}% "
                f"| {s['overclaim_rate']*100:.1f}% | {s['median_tokens']:,} | {s['median_latency_s']} | {s['mean_tool_calls']} |"
            )

    md.extend(["", "## Paper × Condition Breakdown", "| Paper | Condition | n | Clean Success | Mean Rubric | Overclaim | Med. Tokens |", "|---|---|---:|---:|---:|---:|---:|"])
    for p in sorted({r["paper_id"] for r in rows}):
        for c in ["paper_only", "raw_supplements", "companion_v3", "companion_v3_1", "naive_preload"]:
            k = f"{p}|{c}"
            if k not in report_obj["by_paper_condition"]:
                continue
            s = report_obj["by_paper_condition"][k]
            md.append(
                f"| `{p}` | `{c}` | {s['n']} | **{s['clean_rate']*100:.1f}%** | {s['rubric_mean']*100:.1f}% "
                f"| {s['overclaim_rate']*100:.1f}% | {s['median_tokens']:,} |"
            )

    (SUMMARY_DIR / "RESULTS_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    # Export blinded 20% stratified Human Validation Sample (prioritizing disagreements + balanced strata)
    rng = random.Random(20261121)
    target_n = min(180, max(24, int(round(len(rows) * 0.20))))
    disagree_rows = [r for r in rows if r["judge_disagree"]]
    agree_rows = [r for r in rows if not r["judge_disagree"]]
    rng.shuffle(disagree_rows)
    rng.shuffle(agree_rows)
    sample = disagree_rows[: min(len(disagree_rows), target_n // 2)]
    rem = target_n - len(sample)
    # Stratify remaining across (paper_id, stratum)
    buckets = defaultdict(list)
    for r in agree_rows:
        buckets[(r["paper_id"], r["stratum"])].append(r)
    bkeys = sorted(buckets.keys())
    bi = 0
    while len(sample) < target_n and any(buckets.values()):
        bk = bkeys[bi % len(bkeys)]
        if buckets[bk]:
            sample.append(buckets[bk].pop())
        bi += 1
    rng.shuffle(sample)

    trial_text_map = {t["trial_id"]: t["final_answer"] for t in trials}
    h_csv = GRADES_DIR / "HUMAN_VALIDATION_BLIND_SHEET.csv"
    with h_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["blind_id", "paper_id", "qid", "stratum", "question", "rubric_json", "assistant_answer", "human_clean_success_0_1", "human_overclaim_0_1", "human_halluc_0_1", "human_notes"])
        for idx, r in enumerate(sample, 1):
            q = qmap[r["qid"]]
            w.writerow([f"H{idx:03d}", r["paper_id"], r["qid"], r["stratum"], q["question"], json.dumps(q["rubric_items"]), trial_text_map.get(r["trial_id"], ""), "", "", "", ""])
    # Key mapping kept separately so grading stays strictly blind
    key_map = {f"H{idx:03d}": {"trial_id": r["trial_id"], "model": r["model"], "condition": r["condition"], "judge_clean_consensus": r["clean_success"]} for idx, r in enumerate(sample, 1)}
    (GRADES_DIR / "HUMAN_VALIDATION_KEY_SEALED.json").write_text(json.dumps(key_map, indent=2), encoding="utf-8")
    print(f"\nSaved RESULTS_REPORT.md, RESULTS_SUMMARY.json, scored_trials.csv, and blinded {len(sample)}-item HUMAN_VALIDATION_BLIND_SHEET.csv.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(BENCH_ROOT / "config.json"))
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--analyze-only", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    qdata = json.loads((BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))
    qmap = {q["qid"]: q for q in qdata["questions"]}
    trials = load_all_trials()
    print(f"Loaded {len(trials)} completed trials.")

    jA_cfg = cfg["judges"]["A"]
    jB_cfg = cfg["judges"]["B"]
    if args.analyze_only:
        gA = {}
        for l in (GRADES_DIR / "judge_A.jsonl").read_text(encoding="utf-8").splitlines():
            if l.strip():
                obj = json.loads(l)
                if "item_scores" in obj:
                    gA[obj["trial_id"]] = obj
        gB = {}
        for l in (GRADES_DIR / "judge_B.jsonl").read_text(encoding="utf-8").splitlines():
            if l.strip():
                obj = json.loads(l)
                if "item_scores" in obj:
                    gB[obj["trial_id"]] = obj
    else:
        gA = asyncio.run(grade_with_judge("A", jA_cfg["provider"], jA_cfg["id"], trials, qmap, args.concurrency))
        gB = asyncio.run(grade_with_judge("B", jB_cfg["provider"], jB_cfg["id"], trials, qmap, args.concurrency))

    analyze_and_export(trials, gA, gB, qmap)


if __name__ == "__main__":
    main()
