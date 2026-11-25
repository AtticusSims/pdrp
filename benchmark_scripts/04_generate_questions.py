"""Strictly CARD-BLIND multi-stratum benchmark question & atomic rubric generator.

METHODOLOGICAL SAFEGUARD:
  - Reads ONLY corpora/<paper>/article.txt and corpora/<paper>/sources/*.
  - NEVER reads crates/ (COMPANION.md or cards/*.md), eliminating companion-to-question leakage.
  - Uses Anthropic Claude Sonnet 4.6 (distinct model family from the Gemini companion author!).
  - Generates 16 questions per paper (4 per stratum = 64 total):
      A: article_only            (4) — answerable 100% from article.txt alone
      B: supplementary_fact      (4) — requires numbers/parameters/tables present ONLY in sources/
      C: qualification_binding   (4) — requires linking a claim to its critical caveat/exclusion/peer-review objection
      D: temporal_and_abstention (4) — 2 version/revision/post-pub status questions + 2 genuinely unanswerable abstention items
"""
from __future__ import annotations

import json
import re
import time
from importlib import import_module
from pathlib import Path
from typing import Any

from openrouter_client import get_openrouter_client

BENCH_ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = BENCH_ROOT / "corpora"
BENCHMARK_DIR = BENCH_ROOT / "benchmark"

QUESTION_AUTHOR_MODEL = "x-ai/grok-4.6"

SYSTEM_PROMPT = """You are designing a rigorous, strictly source-grounded scientific reading benchmark for evaluating AI research assistants.

You are given ONLY the main article text and its raw supplementary sources (with 1-based line numbers). You have NO knowledge of any companion document.

Design EXACTLY 16 realistic researcher questions for this paper — 4 in each stratum:

1. `article_only` (4 questions: A1..A4):
   - 100% answerable from `article` alone without consulting any supplementary file.
   - Tests precise factual comprehension and methodological reading of the main paper (designed to detect whether supplementary material degrades article comprehension).

2. `supplementary_fact` (4 questions: B1..B4):
   - Requires specific numbers, table rows, exact parameters, coding rules, exclusion counts, or experimental details that are ABSENT from `article` and appear ONLY in `sources/`.
   - Verify explicitly that the required facts are NOT stated in `article`.

3. `qualification_binding` (4 questions: C1..C4):
   - Targets a substantive claim or finding where a crucial limitation, sample/denominator boundary, negative/null control, confound, or peer-review criticism in the supplements/author-response/article materially qualifies how the claim must be interpreted.
   - A naive assistant that states the headline finding without its attached qualification will miss 1-2 required rubric items.

4. `temporal_and_abstention` (4 questions: D1..D4):
   - D1 & D2 (`temporal_status`): Distinguish original/preprint findings from peer-review revisions, follow-up analyses, or post-submission diagnostics (e.g., what changed after review, or what a later check does/does not establish about the original data).
   - D3 & D4 (`calibrated_abstention`): Realistic researcher questions whose requested data/analysis is **genuinely NOT reported anywhere** in either `article` or any supplied source file! (Double-check carefully across the entire provided text that the answer really is absent!) For these two questions, `unanswerable` must be `true` and the rubric items check that the model explicitly identifies the gap and abstains from fabricating values.

RUBRIC RULES (CRITICAL — AVOID BRITTLE PROSE GRADING):
- Every question has 3 to 4 **atomic binary rubric items** (`id`, `criterion`, `evidence_locator`).
- Each criterion must test ONE clear, objective, source-verifiable fact, boundary, or abstention (never penalize benign synonyms or ordinary English wording).
- Include 1-2 concrete `common_error_traps` (specific factual conflations, overclaims, or fabrications a careless model might make).

Return a single valid JSON object:
{
  "paper_id": "...",
  "questions": [
    {
      "qid": "<paper_prefix>-A1",
      "stratum": "article_only|supplementary_fact|qualification_binding|temporal_and_abstention",
      "sub_type": "article|supplement|qualification|temporal|abstention",
      "unanswerable": false,
      "question": "Clear, natural researcher question (1-3 sentences).",
      "rubric_items": [
        {"id": "u1", "criterion": "Exact atomic factual/qualification criterion", "evidence_locator": "source_id:start-end", "verbatim_anchor": "short <=25-word quote from that source (or 'ABSENT' for abstention)"}
      ],
      "common_error_traps": ["Specific overclaim or conflation to flag"]
    }
  ]
}"""


def draft_questions_for_paper(paper_id: str, force: bool = False) -> dict[str, Any]:
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BENCHMARK_DIR / f"questions_{paper_id}.json"
    if out_path.exists() and not force:
        print(f"  [SKIP] {out_path.name} exists.")
        return json.loads(out_path.read_text(encoding="utf-8"))

    author_mod = import_module("02_author_companions")
    corpus_dir = CORPORA_DIR / paper_id
    # Strictly source-only context (NEVER reads crates/!)
    context = author_mod.build_numbered_context(corpus_dir, max_total_chars=260_000)

    prefix_map = {
        "digital-creativity": "DC",
        "jcal-review": "JCAL",
        "elife-111304": "EL1",
        "elife-110672": "EL2",
    }
    pref = prefix_map[paper_id]
    print(f"Drafting 16 card-blind questions for {paper_id} with {QUESTION_AUTHOR_MODEL} (~{len(context):,} chars)...", flush=True)

    client = get_openrouter_client(async_mode=False, timeout=240.0)
    t0 = time.time()
    resp = client.chat.completions.create(
        model=QUESTION_AUTHOR_MODEL,
        temperature=0.1,
        max_tokens=12000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Generate exactly 16 questions for paper `{paper_id}` using IDs `{pref}-A1`..`{pref}-A4`, "
                    f"`{pref}-B1`..`{pref}-B4`, `{pref}-C1`..`{pref}-C4`, `{pref}-D1`..`{pref}-D4` "
                    "(where D3 and D4 are `unanswerable: true` calibrated-abstention questions).\n"
                    "Double-check every `evidence_locator` and `verbatim_anchor` directly against the numbered lines below.\n"
                    "Return ONLY the raw valid JSON object (no surrounding explanation).\n\n"
                    + context
                ),
            },
        ],
    )
    elapsed = round(time.time() - t0, 2)
    raw_full = (resp.choices[0].message.content or "").strip()
    i0 = raw_full.find("{")
    i1 = raw_full.rfind("}")
    if i0 == -1 or i1 == -1:
        raise RuntimeError(f"Model returned no JSON object (len={len(raw_full)}): {raw_full[:300]!r}")
    payload = json.loads(raw_full[i0 : i1 + 1])
    payload["paper_id"] = paper_id
    payload["_meta"] = {
        "question_author_model": QUESTION_AUTHOR_MODEL,
        "card_blind": True,
        "elapsed_seconds": elapsed,
        "prompt_tokens": getattr(resp.usage, "prompt_tokens", 0) if resp.usage else 0,
        "completion_tokens": getattr(resp.usage, "completion_tokens", 0) if resp.usage else 0,
    }
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"  DONE {paper_id}: {len(payload.get('questions', []))} questions in {elapsed}s", flush=True)
    return payload


def verify_and_merge(papers: list[str]) -> None:
    """Verify every question's locators and merge into benchmark/questions.json."""
    all_q: list[dict[str, Any]] = []
    issues: list[str] = []
    for pid in papers:
        p = BENCHMARK_DIR / f"questions_{pid}.json"
        data = json.loads(p.read_text(encoding="utf-8"))
        meta = json.loads((CORPORA_DIR / pid / "metadata.json").read_text(encoding="utf-8"))
        valid_sids = {"article": meta["article"]["lines"]}
        for sm in meta["sources"]:
            valid_sids[sm["source_id"]] = sm["lines"]
        for q in data["questions"]:
            q["paper_id"] = pid
            all_q.append(q)
            for u in q.get("rubric_items", []):
                loc = str(u.get("evidence_locator", "")).strip()
                if q.get("unanswerable") or loc.upper() in ("ABSENT", "NONE", "N/A", ""):
                    continue
                m = re.match(r"^([A-Za-z0-9_.-]+):(\d+)(?:-(\d+))?$", loc)
                if not m:
                    issues.append(f"{q['qid']}.{u['id']}: non-standard locator '{loc}'")
                elif m.group(1) not in valid_sids:
                    issues.append(f"{q['qid']}.{u['id']}: unknown source_id '{m.group(1)}'")
                elif int(m.group(2)) > valid_sids[m.group(1)]:
                    issues.append(f"{q['qid']}.{u['id']}: start line {m.group(2)} > max {valid_sids[m.group(1)]}")

    merged = {
        "schema": "companion-v3-benchmark-questions/1.0",
        "total_questions": len(all_q),
        "papers": papers,
        "locator_warnings": issues,
        "questions": all_q,
    }
    (BENCHMARK_DIR / "questions.json").write_text(json.dumps(merged, indent=2), encoding="utf-8")
    print(f"\nMerged {len(all_q)} questions into benchmark/questions.json ({len(issues)} locator warnings).")
    for w in issues[:12]:
        print("  WARN:", w)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", nargs="*", default=["digital-creativity", "jcal-review", "elife-111304", "elife-110672"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(lambda pid: draft_questions_for_paper(pid, force=args.force), args.papers))
    verify_and_merge(args.papers)


if __name__ == "__main__":
    main()
