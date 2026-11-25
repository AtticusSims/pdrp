"""Author-side Companion v3 generator using Gemini (via OpenRouter).

Produces an RO-Crate-compatible progressive-disclosure companion for each frozen paper:
  - ro-crate-metadata.json (RO-Crate 1.1/schema.org JSON-LD manifest)
  - COMPANION.md           (strictly <= 2,500 bytes routing manifest, Layer 0)
  - cards/*.md             (14-20 atomic 150-350 word YAML+Markdown cards, Layer 1)
  - authoring_receipt.json (exact model, prompt/completion tokens, latency, USD estimate)
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openrouter_client import get_openrouter_client

BENCH_ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = BENCH_ROOT / "corpora"
CRATES_DIR = BENCH_ROOT / "crates"

AUTHOR_MODEL = "google/gemini-4-neon"

SYSTEM_PROMPT = """You are an expert scholarly communication architect authoring an AI-Readable Research Companion (Protocol v3) for an academic paper and its raw supplementary sources.

Your design objective is MAXIMUM SIGNAL, ZERO BUREAUCRATIC FILLER:
- An AI assistant reading this paper will ONLY see `COMPANION.md` (<= 2,300 bytes) alongside the main article text. It will open specific atomic cards via `read_card(card_id)` only when a reader's question touches supplementary methods, exact data/denominators, caveats/qualifications, peer-review critiques, or post-publication updates.
- When `read_card(card_id)` is called, the runtime automatically appends any cards listed in `linked_cards` or targeted by `qualifies`/`conflicts_with`/`updates` relations. Use that! Keep major caveats, sample exclusions, null results, and reviewer criticisms in dedicated `Q##` / `U##` cards AND link them directly to the `C##` / `M##` / `D##` cards they qualify.

STRICT RULES:
1. Ground EVERY fact, number, denominator, p-value, sample size, and quote in the supplied article and supplementary sources. NEVER invent numbers, dates, or citations.
2. Cite exact `source_id:start-end` line ranges (1-based) from the numbered sources provided.
3. ZERO defensive legalese or repetitive meta-disclaimers (do NOT write "This guide makes no efficacy claim", "No independent theoretical genealogy is inferred", etc.). Write crisp, dense scientific prose.
4. Keep `COMPANION.md` STRICTLY under 2,300 bytes UTF-8. It must contain:
   - Paper title, edition/date, and temporal status (submitted / published VOR / post-submission diagnostics)
   - A 3-5 bullet **Coverage Map** explicitly stating (a) what ONLY exists in supplements/reviews/tables and (b) what is explicitly ABSENT / private / not reported in the corpus
   - A flat 1-line **Card Index** listing every card ID, type, title, and 3-5 search keywords.
5. Produce 14 to 20 atomic cards (`cards/*.md`), each 140 to 320 words, covering:
   - Core claims & empirical findings (`C01`, `C02`, ...) — especially any nuances, multi-phase results, or negative/null findings
   - Methods, instruments, coding/screening protocols, hyperparameters, input conventions (`M01`, `M02`, ...) — especially details residing ONLY in supplements/tables/checklists
   - Exact datasets, populations, denominators, exclusions, missingness accounting (`D01`, `D02`, ...)
   - Critical qualifications, limitations, confounds, and peer-review objections/dispositions (`Q01`, `Q02`, ...)
   - Post-publication / revision / diagnostic updates (`U01`, `U02`, ...) distinguishing original version vs. later checks or reviewer-driven revisions.
6. Use ONLY our 6-relation vocabulary in card frontmatter: `supports`, `qualifies`, `derived_from`, `uses`, `conflicts_with`, `responds_to`.

OUTPUT FORMAT:
Return a single valid JSON object (no markdown fences outside JSON) with exact keys:
{
  "companion_md": "<string, <= 2300 bytes>",
  "cards": [
    {
      "id": "C01",
      "filename": "C01-short-slug.md",
      "title": "Concise descriptive title",
      "type": "claim|method|data|qualification|review_disposition|update",
      "temporal_status": "original_article|original_supplement|peer_review_revision|post_submission_diagnostic",
      "source_locators": ["article:12-30", "S03:400-445"],
      "relations": [{"type": "qualifies", "target": "C01", "basis": "one short phrase"}],
      "linked_cards": ["Q01"],
      "body": "Concise 140-320 word markdown body with exact numbers, denominators, scope, and source locators."
    }
  ]
}"""


def build_numbered_context(corpus_dir: Path, max_total_chars: int = 420_000) -> str:
    """Assemble numbered article + all supplementary sources within Gemini's 1M context window."""
    meta = json.loads((corpus_dir / "metadata.json").read_text(encoding="utf-8"))
    parts: list[str] = []
    parts.append(f"PAPER METADATA:\n{json.dumps({k: meta[k] for k in ['paper_id','title','authors','date','genre','license','doi'] if k in meta}, indent=2)}\n")

    art_lines = (corpus_dir / "article.txt").read_text(encoding="utf-8").splitlines()
    numbered_art = "\n".join(f"{i}: {ln}" for i, ln in enumerate(art_lines, 1))
    parts.append(f"\n=== SOURCE: article ({len(art_lines)} lines) ===\n{numbered_art}\n")

    used = sum(len(p) for p in parts)
    # Prioritize supplements, peer reviews, author responses, data tables, diagnostics, checklists first
    role_priority = {
        "supplement": 1,
        "peer_review_assessment": 1,
        "peer_review": 1,
        "author_response": 1,
        "data_table": 2,
        "post_submission_diagnostic": 2,
        "review_record": 2,
        "checklist": 3,
        "figure_text": 3,
        "research_record": 4,
        "instrument_or_code": 5,
    }
    ordered_sources = sorted(meta["sources"], key=lambda s: (role_priority.get(s["role"], 9), s["bytes"]))
    included_ids = []
    skipped_ids = []
    for sm in ordered_sources:
        sid = sm["source_id"]
        sp = corpus_dir / sm["relpath"]
        lines = sp.read_text(encoding="utf-8", errors="replace").splitlines()
        block = f"\n=== SOURCE: {sid} | role={sm['role']} | title={sm['title']} ({len(lines)} lines) ===\n"
        # Cap individual huge raw code/log files at 400 lines so all supplements fit cleanly
        if len(lines) > 550 and sm["role"] in ("instrument_or_code", "research_record"):
            shown = lines[:300] + [f"... [{len(lines)-400} middle lines omitted; inspect if needed] ..."] + lines[-100:]
            numbered = "\n".join(f"{i}: {ln}" for i, ln in enumerate(lines[:300], 1))
            numbered += f"\n... [lines 301-{len(lines)-100} omitted] ...\n"
            numbered += "\n".join(f"{len(lines)-100+i}: {ln}" for i, ln in enumerate(lines[-100:], 1))
        else:
            numbered = "\n".join(f"{i}: {ln}" for i, ln in enumerate(lines, 1))
        entry = block + numbered + "\n"
        if used + len(entry) > max_total_chars:
            skipped_ids.append(f"{sid} ({sm['title']}, {len(lines)}L)")
            continue
        parts.append(entry)
        used += len(entry)
        included_ids.append(sid)

    if skipped_ids:
        parts.append("\nADDITIONAL SOURCES IN ARCHIVE (not inlined due to prompt budget):\n- " + "\n- ".join(skipped_ids))
    return "".join(parts)


def render_card_md(card: dict[str, Any]) -> str:
    import yaml

    fm = {
        "id": card["id"],
        "title": card["title"],
        "type": card["type"],
        "temporal_status": card.get("temporal_status", "original_article"),
        "source_locators": card.get("source_locators", []),
        "relations": card.get("relations", []),
        "linked_cards": card.get("linked_cards", []),
    }
    header = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{header}\n---\n\n# {card['id']}: {card['title']}\n\n{card['body'].strip()}\n"


def build_rocrate_metadata(meta: dict[str, Any], crate_dir: Path, cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a valid RO-Crate 1.1 JSON-LD manifest describing the companion package."""
    has_part: list[dict[str, str]] = [{"@id": "COMPANION.md"}]
    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
            "about": {"@id": "./"},
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": f"AI Research Companion (v3) for: {meta['title']}",
            "description": "Progressive-disclosure RO-Crate research companion containing a <=2.5 KB routing manifest (COMPANION.md), atomic qualification-bound knowledge cards (cards/), and provenance links to frozen original sources.",
            "datePublished": meta.get("date", "2026-11-21"),
            "license": meta.get("license", "CC-BY-4.0"),
            "identifier": meta.get("doi", meta["paper_id"]),
            "author": [{"@type": "Person", "name": a} for a in meta.get("authors", [])],
            "hasPart": has_part,
        },
        {
            "@id": "COMPANION.md",
            "@type": "File",
            "name": "Progressive-Disclosure Companion Routing Manifest",
            "encodingFormat": "text/markdown",
            "sha256": hashlib.sha256((crate_dir / "COMPANION.md").read_bytes()).hexdigest(),
        },
    ]
    for c in cards:
        rel = f"cards/{c['filename']}"
        has_part.append({"@id": rel})
        cp = crate_dir / rel
        graph.append(
            {
                "@id": rel,
                "@type": "File",
                "name": f"{c['id']}: {c['title']}",
                "additionalType": c["type"],
                "encodingFormat": "text/markdown",
                "sha256": hashlib.sha256(cp.read_bytes()).hexdigest() if cp.exists() else "",
            }
        )
    for sm in meta["sources"]:
        rel = f"../../corpora/{meta['paper_id']}/{sm['relpath']}"
        graph.append(
            {
                "@id": f"source:{sm['source_id']}",
                "@type": "File",
                "name": sm["title"],
                "additionalType": sm["role"],
                "sha256": sm["sha256"],
                "contentSize": str(sm["bytes"]),
            }
        )
    return {"@context": "https://w3id.org/ro/crate/1.1/context", "@graph": graph}


def author_one_paper(paper_id: str, force: bool = False) -> dict[str, Any]:
    corpus_dir = CORPORA_DIR / paper_id
    crate_dir = CRATES_DIR / paper_id
    if not force and (crate_dir / "COMPANION.md").exists() and (crate_dir / "ro-crate-metadata.json").exists():
        print(f"  [SKIP] {paper_id} already authored (use --force to regenerate).")
        return json.loads((crate_dir / "audit" / "authoring_receipt.json").read_text(encoding="utf-8"))

    meta = json.loads((corpus_dir / "metadata.json").read_text(encoding="utf-8"))
    context = build_numbered_context(corpus_dir)
    print(f"Authoring {paper_id} with {AUTHOR_MODEL} (input ~{len(context):,} chars)...", flush=True)

    client = get_openrouter_client(async_mode=False, timeout=240.0)
    t0 = time.time()
    resp = client.chat.completions.create(
        model=AUTHOR_MODEL,
        temperature=0.1,
        max_tokens=16000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Author the Progressive-Disclosure Research Companion v3 for `{paper_id}`.\n"
                    "Remember: COMPANION.md MUST be <= 2,300 bytes UTF-8, include a Coverage Map (what is ONLY in supplements/reviews vs. what is ABSENT from the corpus), "
                    "and index 14-20 crisp atomic cards with exact `source_id:start-end` line locators and qualification links.\n\n"
                    + context
                ),
            },
        ],
    )
    elapsed = round(time.time() - t0, 2)
    raw_content = resp.choices[0].message.content or ""
    # Strip accidental markdown json fences if any
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_content.strip(), flags=re.S)
    payload = json.loads(cleaned)

    # Save v0 snapshot before any later adversarial repair
    cards_dir = crate_dir / "cards"
    audit_dir = crate_dir / "audit"
    v0_dir = audit_dir / "v0_initial_draft"
    cards_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    v0_dir.mkdir(parents=True, exist_ok=True)

    # Clear old cards if regenerating
    for old in cards_dir.glob("*.md"):
        old.unlink()

    companion_md = payload["companion_md"].strip() + "\n"
    (crate_dir / "COMPANION.md").write_text(companion_md, encoding="utf-8")
    (v0_dir / "COMPANION.md").write_text(companion_md, encoding="utf-8")

    cards = payload["cards"]
    for c in cards:
        safe_fn = re.sub(r"[^A-Za-z0-9._-]+", "-", c.get("filename") or f"{c['id']}.md")
        if not safe_fn.endswith(".md"):
            safe_fn += ".md"
        c["filename"] = safe_fn
        md_txt = render_card_md(c)
        (cards_dir / safe_fn).write_text(md_txt, encoding="utf-8")
        (v0_dir / safe_fn).write_text(md_txt, encoding="utf-8")

    rocrate = build_rocrate_metadata(meta, crate_dir, cards)
    (crate_dir / "ro-crate-metadata.json").write_text(json.dumps(rocrate, indent=2), encoding="utf-8")

    usage = resp.usage
    prompt_tok = getattr(usage, "prompt_tokens", 0) if usage else 0
    comp_tok = getattr(usage, "completion_tokens", 0) if usage else 0
    cost_usd = round((prompt_tok * 3.0 + comp_tok * 15.0) / 1e6, 4)

    receipt = {
        "paper_id": paper_id,
        "author_model": AUTHOR_MODEL,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": elapsed,
        "prompt_tokens": prompt_tok,
        "completion_tokens": comp_tok,
        "estimated_cost_usd": cost_usd,
        "companion_md_bytes": (crate_dir / "COMPANION.md").stat().st_size,
        "card_count": len(cards),
        "card_ids": [c["id"] for c in cards],
    }
    (audit_dir / "authoring_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(
        f"  DONE {paper_id}: COMPANION.md={receipt['companion_md_bytes']}B | {len(cards)} cards | "
        f"{prompt_tok:,} in / {comp_tok:,} out | ~${cost_usd:.3f} | {elapsed}s",
        flush=True,
    )
    return receipt


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", nargs="*", default=["digital-creativity", "jcal-review", "elife-111304", "elife-110672"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    receipts = []
    for pid in args.papers:
        receipts.append(author_one_paper(pid, force=args.force))
    tot_cost = sum(r["estimated_cost_usd"] for r in receipts)
    print(f"\nAuthoring complete across {len(receipts)} papers. Estimated total cost: ${tot_cost:.3f}")


if __name__ == "__main__":
    main()
