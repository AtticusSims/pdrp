"""Supplementary Reasoning On/Off Within-Weight Ablation Runner + Blinded 2-Judge Grader.

Runs strictly isolated into results/reasoning_ablation/ without modifying any file
from the main 2,304-trial dataset or live human validation dashboard.

Models & opposite-reasoning arms:
  1. deepseek/deepseek-v3.2  -> OpenRouter extra_body={"reasoning": {"effort": "medium"}}  (OFF -> ON)
  2. qwen3.8:27b-q4_K_M      -> Ollama think=False                                        (ON -> OFF)
  3. gpt-oss:20b             -> Ollama think="low"                                        (Medium -> Low)

Conditions: raw_supplements, companion_v3, companion_v3_1 (all 64 card-blind questions = 576 trials).
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import numpy as np
from scipy import stats

from openrouter_client import get_openrouter_client
from tools_engine import PaperToolbox
import importlib

m05 = importlib.import_module("05_run_benchmark")
m06 = importlib.import_module("06_grade_and_analyze")

BENCH_ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = BENCH_ROOT / "corpora"
CRATES_DIR = BENCH_ROOT / "crates"
BENCHMARK_DIR = BENCH_ROOT / "benchmark"
MAIN_SCORED_CSV = BENCH_ROOT / "results" / "summary" / "scored_trials.csv"

ABL_ROOT = BENCH_ROOT / "results" / "reasoning_ablation"
ABL_RAW = ABL_ROOT / "raw"
ABL_GRADES = ABL_ROOT / "grades"
ABL_SUMMARY = ABL_ROOT / "summary"

OLLAMA_API_CHAT = "http://127.0.0.1:11434/api/chat"
MAX_TOOL_TURNS = 8
MAX_OUTPUT_TOKENS = 8192

ABLATION_SPECS: dict[str, dict[str, Any]] = {
    "deepseek/deepseek-v3.2": {
        "provider": "openrouter",
        "arm_tag": "reason_on",
        "baseline_reasoning": "OFF (default r_tok=0)",
        "ablation_reasoning": "ON (effort=medium)",
        "extra_body": {"reasoning": {"effort": "medium"}},
        "price_in": 0.26,
        "price_out": 0.38,
    },
    "qwen3.8:27b-q4_K_M": {
        "provider": "ollama",
        "arm_tag": "think_off",
        "baseline_reasoning": "ON (default think=True)",
        "ablation_reasoning": "OFF (think=False)",
        "ollama_think": False,
        "num_ctx": 40960,
        "price_in": 0.0,
        "price_out": 0.0,
    },
    "gpt-oss:20b": {
        "provider": "ollama",
        "arm_tag": "think_low",
        "baseline_reasoning": "Medium (default)",
        "ablation_reasoning": "Low (think='low')",
        "ollama_think": "low",
        "num_ctx": 49152,
        "price_in": 0.0,
        "price_out": 0.0,
    },
}

CONDITIONS = ["raw_supplements", "companion_v3", "companion_v3_1"]


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s)


async def run_ablation_trial(
    client: Any,
    spec: dict[str, Any],
    model_id: str,
    tb: PaperToolbox,
    qobj: dict[str, Any],
) -> dict[str, Any]:
    provider = spec["provider"]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": m05.BASE_SYSTEM_PROMPT},
        {"role": "user", "content": m05.build_user_prompt(tb, qobj["question"])},
    ]
    tools = tb.openai_tool_schemas()
    tool_trace: list[dict[str, Any]] = []
    seen_cards: set[str] = set()
    prompt_tokens = 0
    completion_tokens = 0
    reasoning_tokens = 0
    t0 = time.time()
    final_answer = ""
    error_msg: str | None = None
    turns = 0

    for turn in range(1, MAX_TOOL_TURNS + 2):
        turns = turn
        allow_tools = bool(tools) and (turn <= MAX_TOOL_TURNS)
        if not allow_tools and tools and turn > MAX_TOOL_TURNS:
            messages.append(
                {
                    "role": "user",
                    "content": "You have reached the tool-call limit. Provide your final concise answer now based strictly on the evidence gathered so far.",
                }
            )

        content = ""
        normalized_calls: list[tuple[str, str, dict[str, Any], str]] = []

        if provider == "ollama":
            payload: dict[str, Any] = {
                "model": model_id,
                "stream": False,
                "keep_alive": "15m",
                "think": spec["ollama_think"],
                "messages": messages,
                "options": {
                    "num_ctx": spec["num_ctx"],
                    "temperature": 0.0,
                    "num_predict": MAX_OUTPUT_TOKENS,
                    "seed": 20261121,
                },
            }
            if allow_tools:
                payload["tools"] = tools
            try:
                resp = await client.post(OLLAMA_API_CHAT, json=payload)
                resp.raise_for_status()
                data = resp.json()
                msg = data.get("message") or {}
                content = (msg.get("content") or "").strip()
                reasoning_tokens += len(msg.get("thinking") or "")  # char proxy for local
                prompt_tokens += int(data.get("prompt_eval_count") or 0)
                completion_tokens += int(data.get("eval_count") or 0)
                for idx, tc in enumerate(msg.get("tool_calls") or []):
                    fn = tc.get("function") or {}
                    fname = str(fn.get("name") or "")
                    fargs = fn.get("arguments")
                    if isinstance(fargs, str):
                        raw_str = fargs
                        try:
                            pargs = json.loads(fargs)
                        except Exception:
                            pargs = {}
                    elif isinstance(fargs, dict):
                        pargs = fargs
                        raw_str = json.dumps(fargs)
                    else:
                        pargs = {}
                        raw_str = "{}"
                    normalized_calls.append((str(tc.get("id") or f"call_{turn}_{idx}"), fname, pargs, raw_str))
            except Exception as e:
                error_msg = f"OLLAMA_ERROR turn {turn}: {type(e).__name__}: {str(e)[:400]}"
                break
        else:
            kwargs: dict[str, Any] = {
                "model": model_id,
                "messages": messages,
                "temperature": 0.0,
                "max_tokens": MAX_OUTPUT_TOKENS,
                "extra_body": spec["extra_body"],
            }
            if allow_tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            resp = None
            last_exc: Exception | None = None
            for attempt in range(1, 4):
                try:
                    resp = await client.chat.completions.create(**kwargs)
                    last_exc = None
                    break
                except Exception as e:
                    last_exc = e
                    await asyncio.sleep(2.0 * attempt)
            if last_exc is not None or resp is None:
                error_msg = f"API_ERROR turn {turn}: {type(last_exc).__name__}: {str(last_exc)[:400]}"
                break

            usage = getattr(resp, "usage", None)
            if usage:
                prompt_tokens += int(getattr(usage, "prompt_tokens", 0) or 0)
                completion_tokens += int(getattr(usage, "completion_tokens", 0) or 0)
                det = getattr(usage, "completion_tokens_details", None)
                if det and getattr(det, "reasoning_tokens", None):
                    reasoning_tokens += int(det.reasoning_tokens)

            msg = resp.choices[0].message
            content = (msg.content or "").strip()
            for idx, tc in enumerate(getattr(msg, "tool_calls", None) or []):
                fname = tc.function.name
                raw_args = tc.function.arguments or "{}"
                try:
                    parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    if not isinstance(parsed_args, dict):
                        parsed_args = {}
                except Exception:
                    parsed_args = {}
                normalized_calls.append((tc.id or f"call_{turn}_{idx}", fname, parsed_args, raw_args if isinstance(raw_args, str) else json.dumps(parsed_args)))

        if normalized_calls and allow_tools:
            if provider == "ollama":
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": [
                            {"type": "function", "function": {"name": fn, "arguments": pargs}}
                            for _, fn, pargs, _ in normalized_calls
                        ],
                    }
                )
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": [
                            {"id": tid, "type": "function", "function": {"name": fn, "arguments": rargs}}
                            for tid, fn, _, rargs in normalized_calls
                        ],
                    }
                )
            for tid, fname, parsed_args, _ in normalized_calls:
                result_str = tb.execute(fname, parsed_args, seen_cards=seen_cards)
                co_ret = []
                m_co = re.search(r"\[co_retrieved_cards:\s*(\[.*?\])\]", result_str)
                if m_co:
                    try:
                        co_ret = json.loads(m_co.group(1).replace("'", '"'))
                    except Exception:
                        pass
                tool_trace.append(
                    {
                        "turn": turn,
                        "name": fname,
                        "args": parsed_args,
                        "result_chars": len(result_str),
                        "co_retrieved_cards": co_ret,
                        "no_hit": '"hits": []' in result_str,
                    }
                )
                if provider == "ollama":
                    messages.append({"role": "tool", "tool_name": fname, "content": result_str})
                else:
                    messages.append({"role": "tool", "tool_call_id": tid, "content": result_str})
            continue

        if not content.strip() and turn <= MAX_TOOL_TURNS:
            messages.append(
                {
                    "role": "user",
                    "content": "Your previous response contained no visible final answer. Provide your concise final answer directly now (120–300 words, citing exact locations).",
                }
            )
            continue
        final_answer = content.strip()
        break

    elapsed = round(time.time() - t0, 2)
    est_cost = round((prompt_tokens * spec["price_in"] + completion_tokens * spec["price_out"]) / 1e6, 5)

    return {
        "qid": qobj["qid"],
        "paper_id": qobj["paper_id"],
        "stratum": qobj["stratum"],
        "sub_type": qobj.get("sub_type", ""),
        "unanswerable": bool(qobj.get("unanswerable", False)),
        "provider": provider,
        "model": model_id,
        "arm_tag": spec["arm_tag"],
        "condition": tb.condition,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "latency_seconds": elapsed,
        "turns": turns,
        "tool_call_count": len(tool_trace),
        "tool_trace": tool_trace,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_metric": reasoning_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated_cost_usd": est_cost,
        "final_answer": final_answer,
        "error": error_msg,
    }


async def run_model_ablation(model_id: str, questions: list[dict[str, Any]], concurrency: int) -> None:
    ABL_RAW.mkdir(parents=True, exist_ok=True)
    spec = ABLATION_SPECS[model_id]
    provider = spec["provider"]
    arm = spec["arm_tag"]
    client = get_openrouter_client(async_mode=True, timeout=180.0) if provider == "openrouter" else httpx.AsyncClient(timeout=360.0)

    paper_ids = sorted({q["paper_id"] for q in questions})
    toolboxes = {(pid, cond): PaperToolbox(CORPORA_DIR / pid, CRATES_DIR / pid, cond) for pid in paper_ids for cond in CONDITIONS}
    sem = asyncio.Semaphore(concurrency if provider == "openrouter" else 1)

    for cond in CONDITIONS:
        out_path = ABL_RAW / f"{slugify(model_id)}__{arm}__{cond}.jsonl"
        done_qids: set[str] = set()
        if out_path.exists():
            for line in out_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    if rec.get("final_answer") and not rec.get("error"):
                        done_qids.add(rec["qid"])
                except Exception:
                    pass
        todo = [q for q in questions if q["qid"] not in done_qids]
        if not todo:
            print(f"  [DONE] {model_id}@{arm} | {cond}: all {len(done_qids)} complete.", flush=True)
            continue

        print(f"  [RUN ] {model_id}@{arm} | {cond}: {len(todo)} pending (done: {len(done_qids)})...", flush=True)
        lock = asyncio.Lock()
        t_start = time.time()
        done_now = 0
        cost_now = 0.0
        errs_now = 0

        async def worker(qobj: dict[str, Any]) -> None:
            nonlocal done_now, cost_now, errs_now
            tb = toolboxes[(qobj["paper_id"], cond)]
            async with sem:
                rec = await run_ablation_trial(client, spec, model_id, tb, qobj)
            async with lock:
                with out_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                done_now += 1
                cost_now += rec["estimated_cost_usd"]
                if rec["error"]:
                    errs_now += 1
                if done_now % 8 == 0 or done_now == len(todo):
                    print(
                        f"    {model_id}@{arm} | {cond}: {done_now}/{len(todo)} "
                        f"| tools_last={rec['tool_call_count']} | r_met={rec['reasoning_metric']} "
                        f"| errs={errs_now} | ~${cost_now:.3f} | {time.time() - t_start:.1f}s",
                        flush=True,
                    )

        await asyncio.gather(*(worker(q) for q in todo))

    if provider == "ollama":
        try:
            await client.post(OLLAMA_API_CHAT, json={"model": model_id, "keep_alive": 0})
        except Exception:
            pass
        await client.aclose()
    else:
        try:
            await client.close()
        except Exception:
            pass


def load_ablation_trials() -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for p in sorted(ABL_RAW.glob("*.jsonl")):
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            k = (rec["model"], rec["arm_tag"], rec["condition"], rec["qid"])
            prev = by_key.get(k)
            if prev is None or (rec.get("final_answer") and not rec.get("error")):
                by_key[k] = rec
    out = list(by_key.values())
    for t in out:
        raw = f"abl|{t['qid']}|{t['model']}|{t['arm_tag']}|{t['condition']}|{t.get('completed_utc','')}"
        t["trial_id"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return out


async def grade_ablation(trials: list[dict[str, Any]], qmap: dict[str, dict[str, Any]], concurrency: int = 20) -> tuple[dict[str, Any], dict[str, Any]]:
    ABL_GRADES.mkdir(parents=True, exist_ok=True)
    # Temporarily redirect 06_grade_and_analyze.GRADES_DIR so main grades stay 100% untouched
    orig_dir = m06.GRADES_DIR
    m06.GRADES_DIR = ABL_GRADES
    try:
        gA = await m06.grade_with_judge("A", "openrouter", "z-ai/glm-5.3", trials, qmap, concurrency=concurrency)
        gB = await m06.grade_with_judge("B", "openrouter", "moonshotai/kimi-k2.5", trials, qmap, concurrency=concurrency)
    finally:
        m06.GRADES_DIR = orig_dir
    return gA, gB


def analyze_ablation(trials: list[dict[str, Any]], gA: dict[str, Any], gB: dict[str, Any]) -> None:
    ABL_SUMMARY.mkdir(parents=True, exist_ok=True)
    # Score ablation trials identically to 06_grade_and_analyze
    abl_rows = []
    ka, kb = [], []
    for t in trials:
        tid = t["trial_id"]
        a, b = gA.get(tid), gB.get(tid)
        if not a or not b:
            continue
        ma, mb = m06.score_metrics(a), m06.score_metrics(b)
        ka.append(int(ma["clean_success"]))
        kb.append(int(mb["clean_success"]))
        abl_rows.append(
            {
                "trial_id": tid,
                "qid": t["qid"],
                "paper_id": t["paper_id"],
                "stratum": t["stratum"],
                "unanswerable": t["unanswerable"],
                "model": t["model"],
                "arm_tag": t["arm_tag"],
                "condition": t["condition"],
                "clean_success": int(ma["clean_success"] and mb["clean_success"]),
                "rubric_fraction": round((ma["rubric_fraction"] + mb["rubric_fraction"]) / 2.0, 4),
                "overclaim": int(ma["overclaim"] or mb["overclaim"]),
                "hallucination": int(ma["hallucination"] or mb["hallucination"]),
                "wrong_abstention": int(ma["wrong_abstention"] or mb["wrong_abstention"]),
                "total_tokens": t["total_tokens"],
                "latency_seconds": t["latency_seconds"],
                "tool_call_count": t["tool_call_count"],
                "card_calls": sum(1 for tc in t.get("tool_trace", []) if tc["name"] == "read_card"),
                "reasoning_metric": t.get("reasoning_metric", 0),
            }
        )

    csv_p = ABL_SUMMARY / "ablation_scored_trials.csv"
    if abl_rows:
        with csv_p.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(abl_rows[0].keys()))
            w.writeheader()
            w.writerows(abl_rows)

    # Load matched main-study baseline rows for the same 3 models
    base_idx: dict[tuple[str, str, str], dict[str, Any]] = {}
    with MAIN_SCORED_CSV.open("r", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["model"] in ABLATION_SPECS and r["condition"] in CONDITIONS:
                base_idx[(r["model"], r["condition"], r["qid"])] = {
                    "clean_success": int(r["clean_success"]),
                    "rubric_fraction": float(r["rubric_fraction"]),
                    "overclaim": int(r["overclaim"]),
                    "hallucination": int(r["hallucination"]),
                    "wrong_abstention": int(r["wrong_abstention"]),
                    "total_tokens": int(r["total_tokens"]),
                    "latency_seconds": float(r["latency_seconds"]),
                    "tool_call_count": int(r["tool_call_count"]),
                    "stratum": r["stratum"],
                    "unanswerable": str(r["unanswerable"]).lower() == "true",
                }
    abl_idx = {(r["model"], r["condition"], r["qid"]): r for r in abl_rows}

    kappa = m06.cohens_kappa(ka, kb)
    md = [
        "# Reasoning On/Off Within-Weight Ablation Results",
        "",
        f"- **Scored ablation trials:** {len(abl_rows)} / 576",
        f"- **Inter-judge agreement (`z-ai/glm-5.3` vs `moonshotai/kimi-k2.5`):** Clean-success Cohen's **κ = {kappa}**",
        "",
        "## 1. Within-Weight Comparison: Native Reasoning vs. Opposite Reasoning Arm",
        "| Model | Reasoning Mode | `raw_supplements` | `companion_v3` | `companion_v3_1` | `v3` vs `raw` Δ (p) | `v3.1` vs `raw` Δ (p) | Stratum-C 0-Tool (`v3 → v3.1`) | Med. Tokens (`raw` / `v3` / `v3.1`) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    summary_obj: dict[str, Any] = {"n_scored": len(abl_rows), "kappa_clean": kappa, "models": {}}

    def mcnemar_p(xs_a, xs_b):
        n10 = sum(a == 1 and b == 0 for a, b in zip(xs_a, xs_b))
        n01 = sum(a == 0 and b == 1 for a, b in zip(xs_a, xs_b))
        p = float(stats.binomtest(min(n10, n01), n10 + n01, 0.5).pvalue) if (n10 + n01) else 1.0
        return n10, n01, p

    for mid, spec in ABLATION_SPECS.items():
        summary_obj["models"][mid] = {}
        for mode_lbl, src_idx in [(spec["baseline_reasoning"], base_idx), (spec["ablation_reasoning"], abl_idx)]:
            qids = sorted({q for (m, c, q) in src_idx if m == mid and c == "raw_supplements"})
            if not qids:
                continue
            r_raw = [src_idx[(mid, "raw_supplements", q)] for q in qids if (mid, "raw_supplements", q) in src_idx]
            r_v3 = [src_idx[(mid, "companion_v3", q)] for q in qids if (mid, "companion_v3", q) in src_idx]
            r_v31 = [src_idx[(mid, "companion_v3_1", q)] for q in qids if (mid, "companion_v3_1", q) in src_idx]
            c_raw = np.mean([x["clean_success"] for x in r_raw]) * 100
            c_v3 = np.mean([x["clean_success"] for x in r_v3]) * 100
            c_v31 = np.mean([x["clean_success"] for x in r_v31]) * 100
            _, _, p3 = mcnemar_p([x["clean_success"] for x in r_v3], [x["clean_success"] for x in r_raw])
            _, _, p31 = mcnemar_p([x["clean_success"] for x in r_v31], [x["clean_success"] for x in r_raw])
            zC3 = sum(1 for x in r_v3 if x["stratum"] == "qualification_binding" and x["tool_call_count"] == 0)
            zC31 = sum(1 for x in r_v31 if x["stratum"] == "qualification_binding" and x["tool_call_count"] == 0)
            t_raw = int(np.median([x["total_tokens"] for x in r_raw]))
            t_v3 = int(np.median([x["total_tokens"] for x in r_v3]))
            t_v31 = int(np.median([x["total_tokens"] for x in r_v31]))
            md.append(
                f"| `{mid}` | {mode_lbl} | **{c_raw:.1f}%** | **{c_v3:.1f}%** | **{c_v31:.1f}%** "
                f"| {c_v3-c_raw:+.1f} pp ({p3:.3g}) | {c_v31-c_raw:+.1f} pp ({p31:.3g}) | {zC3} → {zC31}/16 | {t_raw:,} / {t_v3:,} / {t_v31:,} |"
            )
            summary_obj["models"][mid][mode_lbl] = {
                "raw": round(c_raw, 1), "v3": round(c_v3, 1), "v3_1": round(c_v31, 1),
                "p_v3_vs_raw": round(p3, 4), "p_v31_vs_raw": round(p31, 4),
                "zC_v3": zC3, "zC_v31": zC31,
                "med_tok": {"raw": t_raw, "v3": t_v3, "v3_1": t_v31},
            }

    # Pooled High-Reasoning vs Low/No-Reasoning 2x3 Interaction Table across all 3 models!
    md.extend(["", "## 2. Pooled Within-Weight 2×3 Reasoning Interaction (All 3 Models, n=192 Pairs/Cell)", "| Reasoning Regime | `raw_supplements` | `companion_v3` | `companion_v3_1` | `v3` vs `raw` (McNemar p) | `v3.1` vs `raw` (McNemar p) | `D_abstention` (`raw` vs `v3` vs `v3.1`) |", "|---|---:|---:|---:|---:|---:|---:|"])
    # For DeepSeek: ablation=HIGH, baseline=LOW; for Qwen27B & gpt-oss: baseline=HIGH, ablation=LOW
    regimes = {
        "Reasoning ON / Higher": [
            ("deepseek/deepseek-v3.2", abl_idx),
            ("qwen3.8:27b-q4_K_M", base_idx),
            ("gpt-oss:20b", base_idx),
        ],
        "Reasoning OFF / Lower": [
            ("deepseek/deepseek-v3.2", base_idx),
            ("qwen3.8:27b-q4_K_M", abl_idx),
            ("gpt-oss:20b", abl_idx),
        ],
    }
    summary_obj["pooled_regimes"] = {}
    for reg_name, pairs_src in regimes.items():
        all_raw, all_v3, all_v31 = [], [], []
        for mid, src in pairs_src:
            qids = sorted({q for (m, c, q) in src if m == mid and c == "raw_supplements"})
            for q in qids:
                if (mid, "raw_supplements", q) in src and (mid, "companion_v3", q) in src and (mid, "companion_v3_1", q) in src:
                    all_raw.append(src[(mid, "raw_supplements", q)])
                    all_v3.append(src[(mid, "companion_v3", q)])
                    all_v31.append(src[(mid, "companion_v3_1", q)])
        if not all_raw:
            continue
        cr = np.mean([x["clean_success"] for x in all_raw]) * 100
        c3 = np.mean([x["clean_success"] for x in all_v3]) * 100
        c31 = np.mean([x["clean_success"] for x in all_v31]) * 100
        g3, l3, p3 = mcnemar_p([x["clean_success"] for x in all_v3], [x["clean_success"] for x in all_raw])
        g31, l31, p31 = mcnemar_p([x["clean_success"] for x in all_v31], [x["clean_success"] for x in all_raw])
        da_r = np.mean([x["clean_success"] for x in all_raw if x["unanswerable"]]) * 100
        da_3 = np.mean([x["clean_success"] for x in all_v3 if x["unanswerable"]]) * 100
        da_31 = np.mean([x["clean_success"] for x in all_v31 if x["unanswerable"]]) * 100
        md.append(
            f"| **{reg_name}** (n={len(all_raw)}) | **{cr:.1f}%** | **{c3:.1f}%** | **{c31:.1f}%** "
            f"| **{c3-cr:+.1f} pp** (+{g3}/-{l3}, *p*={p3:.4g}) | **{c31-cr:+.1f} pp** (+{g31}/-{l31}, *p*={p31:.4g}) "
            f"| {da_r:.1f}% vs {da_3:.1f}% vs {da_31:.1f}% |"
        )
        summary_obj["pooled_regimes"][reg_name] = {
            "n": len(all_raw), "raw": round(cr, 1), "v3": round(c3, 1), "v3_1": round(c31, 1),
            "v3_vs_raw_delta": round(c3 - cr, 1), "v3_vs_raw_p": round(p3, 5),
            "v31_vs_raw_delta": round(c31 - cr, 1), "v31_vs_raw_p": round(p31, 5),
            "d_abstention": {"raw": round(da_r, 1), "v3": round(da_3, 1), "v3_1": round(da_31, 1)},
        }

    (ABL_SUMMARY / "REASONING_ABLATION_REPORT.json").write_text(json.dumps(summary_obj, indent=2), encoding="utf-8")
    (ABL_SUMMARY / "REASONING_ABLATION_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n" + "\n".join(md))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=list(ABLATION_SPECS.keys()))
    ap.add_argument("--concurrency", type=int, default=10)
    ap.add_argument("--grade-only", action="store_true")
    args = ap.parse_args()

    qdata = json.loads((BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))
    questions = qdata["questions"]
    qmap = {q["qid"]: q for q in questions}

    if not args.grade_only:
        for mid in args.models:
            asyncio.run(run_model_ablation(mid, questions, args.concurrency))

    trials = load_ablation_trials()
    print(f"\nLoaded {len(trials)} ablation trials for grading.")
    if trials and (args.grade_only or len(args.models) == len(ABLATION_SPECS)):
        gA, gB = asyncio.run(grade_ablation(trials, qmap, concurrency=20))
        analyze_ablation(trials, gA, gB)


if __name__ == "__main__":
    main()
