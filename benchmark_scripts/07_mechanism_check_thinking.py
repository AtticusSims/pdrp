"""Within-weight reasoning-mode mechanism check (DP5 Gate-Sensitivity Asymmetry).

Runs ONLY `companion_v3` and `companion_v3_1` across all 64 card-blind questions
with flipped reasoning modes on 3 models that support clean native toggles:
  - deepseek/deepseek-v3.2  (OpenRouter): reasoning.enabled = True  [default was OFF]
  - qwen3.8:27b-q4_K_M      (Ollama GPU): think = False             [default was ON/medium]
  - gemma4:31b-it-qat       (Ollama GPU): think = False             [default was ON/true]

Strictly isolated in results/mechanism_check_thinking/ so the sealed 2,304-trial
main study and its 180-item HUMAN_VALIDATION_BLIND_SHEET.csv remain 100% untouched.
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any

import httpx
import numpy as np
from scipy import stats

from openrouter_client import get_openrouter_client
from tools_engine import PaperToolbox

m05 = import_module("05_run_benchmark")
m06 = import_module("06_grade_and_analyze")

BENCH_ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = BENCH_ROOT / "corpora"
CRATES_DIR = BENCH_ROOT / "crates"
BENCHMARK_DIR = BENCH_ROOT / "benchmark"
MAIN_SUMMARY_CSV = BENCH_ROOT / "results" / "summary" / "scored_trials.csv"

MECH_ROOT = BENCH_ROOT / "results" / "mechanism_check_thinking"
RAW_DIR = MECH_ROOT / "raw"
GRADES_DIR = MECH_ROOT / "grades"
SUMMARY_DIR = MECH_ROOT / "summary"

SPECS = [
    {
        "tag": "deepseek_v3.2__think_on",
        "base_model": "deepseek/deepseek-v3.2",
        "provider": "openrouter",
        "reasoning_mode": "on",
        "price_in": 0.26,
        "price_out": 0.38,
        "num_ctx": 0,
    },
    {
        "tag": "qwen3.8_27b__think_off",
        "base_model": "qwen3.8:27b-q4_K_M",
        "provider": "ollama",
        "reasoning_mode": "off",
        "price_in": 0.0,
        "price_out": 0.0,
        "num_ctx": 49152,
    },
    {
        "tag": "gemma4_31b__think_off",
        "base_model": "gemma4:31b-it-qat",
        "provider": "ollama",
        "reasoning_mode": "off",
        "price_in": 0.0,
        "price_out": 0.0,
        "num_ctx": 40960,
    },
]

CONDITIONS = ["companion_v3", "companion_v3_1"]


async def call_ollama_toggled(
    http_client: httpx.AsyncClient,
    model_id: str,
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None,
    ollama_num_ctx: int,
    think_flag: bool,
) -> tuple[str, list[dict[str, Any]], int, int]:
    payload: dict[str, Any] = {
        "model": model_id,
        "stream": False,
        "think": think_flag,
        "keep_alive": "15m",
        "messages": messages,
        "options": {
            "num_ctx": ollama_num_ctx,
            "temperature": 0.0,
            "num_predict": m05.MAX_OUTPUT_TOKENS,
            "seed": 20261121,
        },
    }
    if tools:
        payload["tools"] = tools
    resp = await http_client.post(m05.OLLAMA_API_CHAT, json=payload)
    resp.raise_for_status()
    data = resp.json()
    msg = data.get("message") or {}
    content = (msg.get("content") or "").strip()
    tcalls = msg.get("tool_calls") or []
    p_tok = int(data.get("prompt_eval_count") or 0)
    c_tok = int(data.get("eval_count") or 0)
    return content, tcalls, p_tok, c_tok


async def run_one_trial(
    client: Any,
    spec: dict[str, Any],
    tb: PaperToolbox,
    qobj: dict[str, Any],
) -> dict[str, Any]:
    provider = spec["provider"]
    model_id = spec["base_model"]
    reasoning_on = spec["reasoning_mode"] == "on"

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

    for turn in range(1, m05.MAX_TOOL_TURNS + 2):
        turns = turn
        allow_tools = bool(tools) and (turn <= m05.MAX_TOOL_TURNS)
        if not allow_tools and tools and turn > m05.MAX_TOOL_TURNS:
            messages.append(
                {
                    "role": "user",
                    "content": "You have reached the tool-call limit. Provide your final concise answer now based strictly on the evidence gathered so far.",
                }
            )

        content = ""
        normalized_calls: list[tuple[str, str, dict[str, Any], str]] = []
        extra_assistant_fields: dict[str, Any] = {}

        if provider == "ollama":
            try:
                content, raw_tcalls, pt, ct = await call_ollama_toggled(
                    client, model_id, messages, tools if allow_tools else None, spec["num_ctx"], reasoning_on
                )
                prompt_tokens += pt
                completion_tokens += ct
                for idx, tc in enumerate(raw_tcalls):
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
                    tc_id = str(tc.get("id") or f"call_{turn}_{idx}")
                    normalized_calls.append((tc_id, fname, pargs, raw_str))
            except Exception as e:
                error_msg = f"OLLAMA_ERROR turn {turn}: {type(e).__name__}: {str(e)[:400]}"
                break
        else:
            kwargs: dict[str, Any] = {
                "model": model_id,
                "messages": messages,
                "temperature": 0.0,
                "max_tokens": m05.MAX_OUTPUT_TOKENS,
                "extra_body": {"reasoning": {"enabled": reasoning_on}},
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
                cdet = getattr(usage, "completion_tokens_details", None)
                if cdet and getattr(cdet, "reasoning_tokens", None):
                    reasoning_tokens += int(cdet.reasoning_tokens or 0)

            msg = resp.choices[0].message
            content = (msg.content or "").strip()
            mdump = msg.model_dump()
            if mdump.get("reasoning_details"):
                extra_assistant_fields["reasoning_details"] = mdump["reasoning_details"]
            for idx, tc in enumerate(getattr(msg, "tool_calls", None) or []):
                fname = tc.function.name
                raw_args = tc.function.arguments or "{}"
                try:
                    parsed_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                    if not isinstance(parsed_args, dict):
                        parsed_args = {}
                except Exception:
                    parsed_args = {}
                normalized_calls.append(
                    (
                        tc.id or f"call_{turn}_{idx}",
                        fname,
                        parsed_args,
                        raw_args if isinstance(raw_args, str) else json.dumps(parsed_args),
                    )
                )

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
                asst_msg: dict[str, Any] = {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": [
                        {"id": tid, "type": "function", "function": {"name": fn, "arguments": rargs}}
                        for tid, fn, _, rargs in normalized_calls
                    ],
                }
                asst_msg.update(extra_assistant_fields)
                messages.append(asst_msg)

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

        if not content.strip() and turn <= m05.MAX_TOOL_TURNS:
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
        "model": spec["tag"],
        "base_model": model_id,
        "reasoning_mode": spec["reasoning_mode"],
        "condition": tb.condition,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "latency_seconds": elapsed,
        "turns": turns,
        "tool_call_count": len(tool_trace),
        "tool_trace": tool_trace,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "reasoning_tokens": reasoning_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated_cost_usd": est_cost,
        "final_answer": final_answer,
        "error": error_msg,
    }


async def run_spec(spec: dict[str, Any], questions: list[dict[str, Any]], concurrency: int) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    provider = spec["provider"]
    client = (
        get_openrouter_client(async_mode=True, timeout=180.0)
        if provider == "openrouter"
        else httpx.AsyncClient(timeout=360.0)
    )
    paper_ids = sorted({q["paper_id"] for q in questions})
    toolboxes = {
        (pid, cond): PaperToolbox(CORPORA_DIR / pid, CRATES_DIR / pid, cond)
        for pid in paper_ids
        for cond in CONDITIONS
    }
    sem = asyncio.Semaphore(concurrency if provider == "openrouter" else 1)

    for cond in CONDITIONS:
        out_path = RAW_DIR / f"{spec['tag']}__{cond}.jsonl"
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
            print(f"  [DONE] {spec['tag']} | {cond}: all {len(done_qids)} complete.", flush=True)
            continue
        print(f"  [RUN ] {spec['tag']} ({provider}, think={spec['reasoning_mode']}) | {cond}: {len(todo)} pending...", flush=True)
        lock = asyncio.Lock()
        t_start = time.time()
        done_now = 0
        errs = 0
        cost = 0.0

        async def worker(qobj: dict[str, Any]) -> None:
            nonlocal done_now, errs, cost
            async with sem:
                rec = await run_one_trial(client, spec, toolboxes[(qobj["paper_id"], cond)], qobj)
            async with lock:
                with out_path.open("a", encoding="utf-8") as fh:
                    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                done_now += 1
                cost += rec["estimated_cost_usd"]
                if rec["error"]:
                    errs += 1
                if done_now % 8 == 0 or done_now == len(todo):
                    print(
                        f"    {spec['tag']} | {cond}: {done_now}/{len(todo)} "
                        f"| tools_last={rec['tool_call_count']} | rtok_last={rec['reasoning_tokens']} "
                        f"| errs={errs} | ~${cost:.3f} | {time.time() - t_start:.1f}s",
                        flush=True,
                    )

        await asyncio.gather(*(worker(q) for q in todo))

    if provider == "ollama":
        try:
            await client.post(m05.OLLAMA_API_CHAT, json={"model": spec["base_model"], "keep_alive": 0})
        except Exception:
            pass
        await client.aclose()
    else:
        try:
            await client.close()
        except Exception:
            pass


def load_mech_trials() -> list[dict[str, Any]]:
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for p in sorted(RAW_DIR.glob("*.jsonl")):
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
        raw = f"{t['qid']}|{t['model']}|{t['condition']}|{t.get('completed_utc', '')}"
        t["trial_id"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return trials


async def grade_mech(
    judge_name: str, model_id: str, trials: list[dict[str, Any]], qmap: dict[str, dict[str, Any]], concurrency: int
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
        print(f"  [DONE] Judge {judge_name}: all {len(existing)} graded.", flush=True)
        return existing

    print(f"  [GRADE] Judge {judge_name} ({model_id}): {len(todo)} pending...", flush=True)
    client = get_openrouter_client(async_mode=True, timeout=180.0)
    sem = asyncio.Semaphore(concurrency)
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
                    try:
                        resp = await client.chat.completions.create(
                            model=model_id,
                            temperature=0.0,
                            max_tokens=3000,
                            extra_body={"reasoning": {"effort": "low"}},
                            messages=[
                                {"role": "system", "content": m06.JUDGE_SYSTEM},
                                {"role": "user", "content": user_msg},
                            ],
                        )
                        parsed = m06.extract_json_object(resp.choices[0].message.content or "")
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
    try:
        await client.close()
    except Exception:
        pass
    return existing


def analyze_mechanism(trials: list[dict[str, Any]], gA: dict[str, dict[str, Any]], gB: dict[str, dict[str, Any]]) -> None:
    SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    ka, kb, ia, ib = [], [], [], []
    for t in trials:
        tid = t["trial_id"]
        a, b = gA.get(tid), gB.get(tid)
        if not a or not b:
            continue
        ma, mb = m06.score_metrics(a), m06.score_metrics(b)
        ka.append(int(ma["clean_success"]))
        kb.append(int(mb["clean_success"]))
        for uid in a["item_scores"]:
            if uid in b["item_scores"]:
                ia.append(a["item_scores"][uid])
                ib.append(b["item_scores"][uid])
        rows.append(
            {
                "trial_id": tid,
                "qid": t["qid"],
                "paper_id": t["paper_id"],
                "stratum": t["stratum"],
                "unanswerable": t["unanswerable"],
                "tag": t["model"],
                "base_model": t["base_model"],
                "reasoning_mode": t["reasoning_mode"],
                "condition": t["condition"],
                "latency_seconds": t["latency_seconds"],
                "tool_call_count": t["tool_call_count"],
                "total_tokens": t["total_tokens"],
                "reasoning_tokens": t.get("reasoning_tokens", 0),
                "rubric_fraction": round((ma["rubric_fraction"] + mb["rubric_fraction"]) / 2.0, 4),
                "clean_success": int(ma["clean_success"] and mb["clean_success"]),
                "hallucination": int(ma["hallucination"] or mb["hallucination"]),
                "overclaim": int(ma["overclaim"] or mb["overclaim"]),
                "wrong_abstention": int(ma["wrong_abstention"] or mb["wrong_abstention"]),
            }
        )

    csv_path = SUMMARY_DIR / "mechanism_scored_trials.csv"
    if rows:
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # Load main-study default baseline rows for the same 3 base models
    main_rows = list(csv.DictReader(MAIN_SUMMARY_CSV.open(encoding="utf-8")))
    default_mode = {
        "deepseek/deepseek-v3.2": "off",
        "qwen3.8:27b-q4_K_M": "on",
        "gemma4:31b-it-qat": "on",
    }
    combined: dict[tuple[str, str, str, str], dict[str, Any]] = {}  # (base_model, mode, cond, qid) -> row
    for r in main_rows:
        bm = r["model"]
        if bm in default_mode and r["condition"] in CONDITIONS:
            combined[(bm, default_mode[bm], r["condition"], r["qid"])] = {
                "clean_success": int(r["clean_success"]),
                "rubric_fraction": float(r["rubric_fraction"]),
                "tool_call_count": int(r["tool_call_count"]),
                "total_tokens": int(r["total_tokens"]),
                "stratum": r["stratum"],
                "overclaim": int(r["overclaim"]),
                "hallucination": int(r["hallucination"]),
            }
    for r in rows:
        combined[(r["base_model"], r["reasoning_mode"], r["condition"], r["qid"])] = {
            "clean_success": int(r["clean_success"]),
            "rubric_fraction": float(r["rubric_fraction"]),
            "tool_call_count": int(r["tool_call_count"]),
            "total_tokens": int(r["total_tokens"]),
            "stratum": r["stratum"],
            "overclaim": int(r["overclaim"]),
            "hallucination": int(r["hallucination"]),
        }

    kappa_c = m06.cohens_kappa(ka, kb)
    kappa_i = m06.cohens_kappa(ia, ib)

    lines = [
        "# Within-Weight Reasoning-Mode Mechanism Check (DP5: Gate-Sensitivity Asymmetry)",
        "",
        f"- **New mechanism-check trials scored:** {len(rows)} / 384",
        f"- **Inter-judge agreement (new trials):** Clean-success κ = **{kappa_c}** | Atomic item-level κ = **{kappa_i}**",
        "",
        "## Within-Model Comparison: Thinking ON vs. Thinking OFF (`companion_v3` vs. `companion_v3_1`)",
        "| Base Model | Mode | `v3.0` Clean | `v3.1` Clean | Δ (`v3.1 − v3.0`) | McNemar *p* | `v3.0→v3.1` Stratum-C 0-Tool | `v3.0→v3.1` Stratum-C Clean | Med. Tokens (`v3.0→v3.1`) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    summary_json: dict[str, Any] = {
        "scored_new_trials": len(rows),
        "kappa_clean": kappa_c,
        "kappa_item": kappa_i,
        "by_model_mode": {},
        "pooled_by_mode": {},
    }

    for bm in ["deepseek/deepseek-v3.2", "qwen3.8:27b-q4_K_M", "gemma4:31b-it-qat"]:
        for mode in ["off", "on"]:
            qids = sorted({q for (m, mo, c, q) in combined if m == bm and mo == mode and c == "companion_v3" and (m, mo, "companion_v3_1", q) in combined})
            if not qids:
                continue
            r3 = [combined[(bm, mode, "companion_v3", q)] for q in qids]
            r31 = [combined[(bm, mode, "companion_v3_1", q)] for q in qids]
            a_b = [x["clean_success"] for x in r31]
            b_b = [x["clean_success"] for x in r3]
            g = sum(x == 1 and y == 0 for x, y in zip(a_b, b_b))
            l = sum(x == 0 and y == 1 for x, y in zip(a_b, b_b))
            pm = float(stats.binomtest(min(g, l), g + l, 0.5).pvalue) if (g + l) > 0 else 1.0
            c3 = [x for x in r3 if x["stratum"] == "qualification_binding"]
            c31 = [x for x in r31 if x["stratum"] == "qualification_binding"]
            zC3 = sum(1 for x in c3 if x["tool_call_count"] == 0)
            zC31 = sum(1 for x in c31 if x["tool_call_count"] == 0)
            sc3 = np.mean([x["clean_success"] for x in c3]) * 100
            sc31 = np.mean([x["clean_success"] for x in c31]) * 100
            t3 = int(np.median([x["total_tokens"] for x in r3]))
            t31 = int(np.median([x["total_tokens"] for x in r31]))
            rate3 = np.mean(b_b) * 100
            rate31 = np.mean(a_b) * 100
            tag_def = " *(default)*" if mode == default_mode[bm] else " *(toggled)*"
            lines.append(
                f"| `{bm}` | **{mode.upper()}**{tag_def} | {rate3:.1f}% | **{rate31:.1f}%** | **{rate31 - rate3:+.1f} pp** (+{g}/−{l}) | {pm:.4g} "
                f"| {zC3}/16 → {zC31}/16 | {sc3:.1f}% → {sc31:.1f}% | {t3:,} → {t31:,} |"
            )
            summary_json["by_model_mode"][f"{bm}|{mode}"] = {
                "n": len(qids),
                "v3_clean": round(rate3, 2),
                "v31_clean": round(rate31, 2),
                "delta_pp": round(rate31 - rate3, 2),
                "gains": g,
                "losses": l,
                "p_mcnemar": round(pm, 6),
                "strC_0tool_v3": zC3,
                "strC_0tool_v31": zC31,
                "strC_clean_v3": round(sc3, 2),
                "strC_clean_v31": round(sc31, 2),
                "med_tok_v3": t3,
                "med_tok_v31": t31,
            }

    lines.extend(["", "## Pooled Within-Weight Contrast Across All 3 Models (`n = 192` Pairs per Mode)", "| Mode | Pairs | `v3.0` Clean | `v3.1` Clean | Δ (`v3.1 − v3.0`) | Gains/Losses | McNemar *p* | Stratum-C 0-Tool (`v3.0→v3.1`) | Stratum-C Clean (`v3.0→v3.1`) |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for mode in ["off", "on"]:
        pairs = [
            (combined[(bm, mode, "companion_v3_1", q)], combined[(bm, mode, "companion_v3", q)])
            for bm in ["deepseek/deepseek-v3.2", "qwen3.8:27b-q4_K_M", "gemma4:31b-it-qat"]
            for q in sorted({q for (m, mo, c, q) in combined if m == bm and mo == mode and c == "companion_v3" and (m, mo, "companion_v3_1", q) in combined})
        ]
        a_b = [p[0]["clean_success"] for p in pairs]
        b_b = [p[1]["clean_success"] for p in pairs]
        g = sum(x == 1 and y == 0 for x, y in zip(a_b, b_b))
        l = sum(x == 0 and y == 1 for x, y in zip(a_b, b_b))
        pm = float(stats.binomtest(min(g, l), g + l, 0.5).pvalue) if (g + l) > 0 else 1.0
        c_pairs = [p for p in pairs if p[0]["stratum"] == "qualification_binding"]
        z3 = sum(1 for p in c_pairs if p[1]["tool_call_count"] == 0)
        z31 = sum(1 for p in c_pairs if p[0]["tool_call_count"] == 0)
        sc3 = np.mean([p[1]["clean_success"] for p in c_pairs]) * 100
        sc31 = np.mean([p[0]["clean_success"] for p in c_pairs]) * 100
        r3, r31 = np.mean(b_b) * 100, np.mean(a_b) * 100
        lines.append(
            f"| **Thinking {mode.upper()}** | {len(pairs)} | {r3:.1f}% | **{r31:.1f}%** | **{r31 - r3:+.1f} pp** | +{g}/−{l} | {pm:.4g} | {z3}/{len(c_pairs)} → {z31}/{len(c_pairs)} | {sc3:.1f}% → {sc31:.1f}% |"
        )
        summary_json["pooled_by_mode"][mode] = {
            "n": len(pairs),
            "v3_clean": round(r3, 2),
            "v31_clean": round(r31, 2),
            "delta_pp": round(r31 - r3, 2),
            "gains": g,
            "losses": l,
            "p_mcnemar": round(pm, 6),
            "strC_0tool_v3": z3,
            "strC_0tool_v31": z31,
            "strC_clean_v3": round(sc3, 2),
            "strC_clean_v31": round(sc31, 2),
        }

    (SUMMARY_DIR / "MECHANISM_CHECK_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (SUMMARY_DIR / "MECHANISM_CHECK_SUMMARY.json").write_text(json.dumps(summary_json, indent=2), encoding="utf-8")
    print(f"\nSaved MECHANISM_CHECK_REPORT.md and MECHANISM_CHECK_SUMMARY.json ({len(rows)} new trials).")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-cloud", action="store_true")
    ap.add_argument("--run-local", action="store_true")
    ap.add_argument("--grade-and-analyze", action="store_true")
    ap.add_argument("--concurrency", type=int, default=10)
    args = ap.parse_args()

    qdata = json.loads((BENCHMARK_DIR / "questions.json").read_text(encoding="utf-8"))
    questions = qdata["questions"]
    qmap = {q["qid"]: q for q in questions}

    if args.run_cloud:
        for sp in SPECS:
            if sp["provider"] == "openrouter":
                asyncio.run(run_spec(sp, questions, args.concurrency))
    if args.run_local:
        for sp in SPECS:
            if sp["provider"] == "ollama":
                asyncio.run(run_spec(sp, questions, 1))
    if args.grade_and_analyze:
        cfg = json.loads((BENCH_ROOT / "config.json").read_text(encoding="utf-8"))
        trials = load_mech_trials()
        print(f"Loaded {len(trials)} mechanism-check trials.")
        gA = asyncio.run(grade_mech("A", cfg["judges"]["A"]["id"], trials, qmap, args.concurrency))
        gB = asyncio.run(grade_mech("B", cfg["judges"]["B"]["id"], trials, qmap, args.concurrency))
        analyze_mechanism(trials, gA, gB)


if __name__ == "__main__":
    main()
