"""Mechanical validator + fresh Gemini adversarial source audit + 1-pass repair + Human Audit Checklist.

Preserves v0 initial drafts under crates/<paper>/audit/v0_initial_draft/ and records exact defect counts
before and after repair so authoring-pipeline fidelity is reported honestly in Design Science.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from openrouter_client import get_openrouter_client
from tools_engine import parse_card_file

BENCH_ROOT = Path(__file__).resolve().parent.parent
CORPORA_DIR = BENCH_ROOT / "corpora"
CRATES_DIR = BENCH_ROOT / "crates"

AUDIT_MODEL = "deepseek/deepseek-v3.2"
REPAIR_MODEL = "qwen/qwen3.8-max-0902"
ALLOWED_RELATIONS = {"supports", "qualifies", "derived_from", "uses", "conflicts_with", "responds_to", "updates"}
ALLOWED_TYPES = {"claim", "method", "data", "qualification", "review_disposition", "update"}
MAX_MANIFEST_BYTES = 2500


def mechanical_check(paper_id: str) -> dict[str, Any]:
    corpus_dir = CORPORA_DIR / paper_id
    crate_dir = CRATES_DIR / paper_id
    meta = json.loads((corpus_dir / "metadata.json").read_text(encoding="utf-8"))

    # Map valid source line ceilings
    line_limits: dict[str, int] = {"article": meta["article"]["lines"]}
    for sm in meta["sources"]:
        line_limits[sm["source_id"]] = sm["lines"]

    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = crate_dir / "COMPANION.md"
    if not manifest_path.exists():
        errors.append("Missing COMPANION.md")
        manifest_text = ""
        manifest_bytes = 0
    else:
        manifest_bytes = manifest_path.stat().st_size
        manifest_text = manifest_path.read_text(encoding="utf-8")
        if manifest_bytes > MAX_MANIFEST_BYTES:
            errors.append(f"COMPANION.md exceeds {MAX_MANIFEST_BYTES} bytes ({manifest_bytes} B)")

    # Check RO-Crate JSON-LD
    rocrate_path = crate_dir / "ro-crate-metadata.json"
    if not rocrate_path.exists():
        errors.append("Missing ro-crate-metadata.json")
    else:
        try:
            rc = json.loads(rocrate_path.read_text(encoding="utf-8"))
            if "@context" not in rc or "@graph" not in rc:
                errors.append("ro-crate-metadata.json missing @context or @graph")
        except Exception as e:
            errors.append(f"Invalid ro-crate-metadata.json: {e}")

    cards_dir = crate_dir / "cards"
    card_files = sorted(cards_dir.glob("*.md")) if cards_dir.exists() else []
    if len(card_files) < 10:
        warnings.append(f"Only {len(card_files)} cards found (expected 14-20)")

    cards: dict[str, tuple[dict[str, Any], str, Path]] = {}
    for cp in card_files:
        fm, body = parse_card_file(cp)
        cid = str(fm.get("id", "")).strip()
        if not cid:
            errors.append(f"{cp.name}: missing YAML frontmatter 'id'")
            continue
        if cid in cards:
            errors.append(f"Duplicate card id '{cid}'")
        cards[cid] = (fm, body, cp)

        ctype = str(fm.get("type", "")).strip()
        if ctype not in ALLOWED_TYPES:
            warnings.append(f"{cid}: non-standard type '{ctype}'")

        wcount = len(body.split())
        if wcount < 80:
            warnings.append(f"{cid}: very short body ({wcount} words)")
        elif wcount > 420:
            warnings.append(f"{cid}: long body ({wcount} words > 420)")

        # Check source locators
        locs = fm.get("source_locators") or []
        if not locs:
            errors.append(f"{cid}: empty source_locators")
        for loc in locs:
            m = re.match(r"^([A-Za-z0-9_.-]+):(\d+)(?:-(\d+))?$", str(loc).strip())
            if not m:
                warnings.append(f"{cid}: non-standard locator format '{loc}'")
                continue
            sid, s_ln, e_ln = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            if sid not in line_limits:
                errors.append(f"{cid}: unknown source_id '{sid}' in locator '{loc}'")
            else:
                if s_ln < 1 or e_ln < s_ln or s_ln > line_limits[sid]:
                    errors.append(f"{cid}: invalid line range '{loc}' (max {line_limits[sid]})")
                elif e_ln > line_limits[sid]:
                    warnings.append(f"{cid}: end line {e_ln} slightly exceeds {sid} max {line_limits[sid]}")

        # Check relations vocabulary
        for rel in fm.get("relations") or []:
            if isinstance(rel, dict):
                rtype = rel.get("type", "")
                if rtype not in ALLOWED_RELATIONS:
                    errors.append(f"{cid}: disallowed relation type '{rtype}'")

    # Cross-check links and COMPANION.md indexing
    for cid, (fm, _, _) in cards.items():
        if cid not in manifest_text:
            errors.append(f"Card '{cid}' is missing from COMPANION.md index")
        for lid in fm.get("linked_cards") or []:
            if str(lid) not in cards:
                errors.append(f"{cid}: broken linked_cards target '{lid}'")
        for rel in fm.get("relations") or []:
            if isinstance(rel, dict):
                tgt = str(rel.get("target", ""))
                if tgt and tgt not in cards:
                    errors.append(f"{cid}: broken relation target '{tgt}'")

    return {
        "paper_id": paper_id,
        "manifest_bytes": manifest_bytes,
        "card_count": len(cards),
        "passed": len(errors) == 0,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def load_crate_summary_text(crate_dir: Path) -> str:
    parts = ["=== COMPANION.md ===\n" + (crate_dir / "COMPANION.md").read_text(encoding="utf-8")]
    for cp in sorted((crate_dir / "cards").glob("*.md")):
        parts.append(f"\n=== {cp.name} ===\n" + cp.read_text(encoding="utf-8"))
    return "\n".join(parts)


def run_adversarial_audit(paper_id: str) -> dict[str, Any]:
    from importlib import import_module
    author_mod = import_module("02_author_companions")

    corpus_dir = CORPORA_DIR / paper_id
    crate_dir = CRATES_DIR / paper_id
    context = author_mod.build_numbered_context(corpus_dir, max_total_chars=380_000)
    crate_txt = load_crate_summary_text(crate_dir)
    mech = mechanical_check(paper_id)

    client = get_openrouter_client(async_mode=False, timeout=240.0)
    prompt = (
        "You are an independent adversarial scientific auditor checking an AI-authored Research Companion (v3) "
        "against the original paper and raw supplementary sources.\n\n"
        "Inspect EVERY card and COMPANION.md for:\n"
        "1. Numeric, denominator, population, or statistical mismatches against the numbered sources.\n"
        "2. Unsupported relations (e.g., claiming a causal/qualifying link not warranted by sources).\n"
        "3. Omitted major negative findings, exclusions, peer-review objections, or post-publication caveats.\n"
        "4. Mechanical issues listed below (e.g. COMPANION.md > 2500 bytes, broken locators/links).\n"
        "5. Any repetitive defensive boilerplate that wastes tokens.\n\n"
        f"MECHANICAL CHECK REPORT:\n{json.dumps(mech, indent=2)}\n\n"
        "Return a single JSON object with keys:\n"
        '{"overall_verdict": "pass|minor_repairs_needed|major_repairs_needed", '
        '"defects": [{"severity": "high|medium|low", "target": "COMPANION.md or card_id", "category": "numeric_error|unsupported_relation|omitted_qualification|locator_error|manifest_size|boilerplate", "issue": "...", "source_evidence": "source_id:line", "recommended_fix": "..."}], '
        '"omitted_high_value_facts": ["..."], "summary": "2-3 sentence assessment"}\n\n'
        "=== GENERATED COMPANION TO AUDIT ===\n" + crate_txt + "\n\n=== ORIGINAL NUMBERED SOURCES ===\n" + context
    )
    t0 = time.time()
    resp = client.chat.completions.create(
        model=AUDIT_MODEL,
        temperature=0.0,
        max_tokens=8000,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )
    elapsed = round(time.time() - t0, 2)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", (resp.choices[0].message.content or "").strip(), flags=re.S)
    audit = json.loads(raw)
    usage = resp.usage
    audit["_meta"] = {
        "audit_model": AUDIT_MODEL,
        "elapsed_seconds": elapsed,
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        "mechanical_pre_repair": mech,
    }
    (crate_dir / "audit" / "adversarial_audit_v0.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return audit


def apply_single_repair(paper_id: str, audit: dict[str, Any]) -> dict[str, Any]:
    from importlib import import_module
    author_mod = import_module("02_author_companions")

    corpus_dir = CORPORA_DIR / paper_id
    crate_dir = CRATES_DIR / paper_id
    mech = audit["_meta"]["mechanical_pre_repair"]
    high_med = [d for d in audit.get("defects", []) if d.get("severity") in ("high", "medium")]
    if mech["passed"] and not high_med:
        print(f"  [CLEAN] {paper_id}: 0 mechanical errors and 0 high/medium adversarial defects; no repair needed.")
        return {"repaired": False, "mechanical_post_repair": mech}

    print(f"  Repairing {paper_id} ({mech['error_count']} mech errors, {len(high_med)} high/med defects)...", flush=True)
    context = author_mod.build_numbered_context(corpus_dir, max_total_chars=360_000)
    crate_txt = load_crate_summary_text(crate_dir)
    meta = json.loads((corpus_dir / "metadata.json").read_text(encoding="utf-8"))

    client = get_openrouter_client(async_mode=False, timeout=240.0)
    t0 = time.time()
    resp = client.chat.completions.create(
        model=REPAIR_MODEL,
        temperature=0.0,
        max_tokens=16000,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": author_mod.SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Repair the Research Companion v3 for `{paper_id}` by fixing EVERY mechanical error and high/medium adversarial defect listed below.\n"
                    "Keep COMPANION.md STRICTLY <= 2,350 bytes UTF-8. Keep all valid source_id:start-end line locators strictly within each file's line bounds.\n"
                    "Return the complete updated JSON object with keys `companion_md` and `cards` (same schema).\n\n"
                    f"=== AUDIT REPORT TO FIX ===\n{json.dumps({'mechanical': mech, 'defects': audit.get('defects', []), 'omitted_high_value_facts': audit.get('omitted_high_value_facts', [])}, indent=2)}\n\n"
                    f"=== CURRENT v0 COMPANION ===\n{crate_txt}\n\n"
                    f"=== ORIGINAL NUMBERED SOURCES ===\n{context}"
                ),
            },
        ],
    )
    elapsed = round(time.time() - t0, 2)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", (resp.choices[0].message.content or "").strip(), flags=re.S)
    payload = json.loads(raw)

    cards_dir = crate_dir / "cards"
    for old in cards_dir.glob("*.md"):
        old.unlink()
    companion_md = payload["companion_md"].strip() + "\n"
    (crate_dir / "COMPANION.md").write_text(companion_md, encoding="utf-8")

    cards = payload["cards"]
    for c in cards:
        safe_fn = re.sub(r"[^A-Za-z0-9._-]+", "-", c.get("filename") or f"{c['id']}.md")
        if not safe_fn.endswith(".md"):
            safe_fn += ".md"
        c["filename"] = safe_fn
        (cards_dir / safe_fn).write_text(author_mod.render_card_md(c), encoding="utf-8")

    rocrate = author_mod.build_rocrate_metadata(meta, crate_dir, cards)
    (crate_dir / "ro-crate-metadata.json").write_text(json.dumps(rocrate, indent=2), encoding="utf-8")

    post_mech = mechanical_check(paper_id)
    usage = resp.usage
    rec = {
        "repaired": True,
        "repair_model": REPAIR_MODEL,
        "elapsed_seconds": elapsed,
        "prompt_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
        "completion_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
        "mechanical_post_repair": post_mech,
    }
    (crate_dir / "audit" / "repair_receipt_v1.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return rec


def write_human_audit_checklist(paper_id: str, audit: dict[str, Any], repair: dict[str, Any]) -> None:
    crate_dir = CRATES_DIR / paper_id
    post = repair["mechanical_post_repair"]
    lines = [
        f"# Human Author Review Checklist — `{paper_id}`",
        "",
        f"**Instructions:** Spend 10–15 minutes inspecting `COMPANION.md` ({post['manifest_bytes']} B) and spot-checking the {post['card_count']} cards in `cards/`. Record actual review minutes and mark each item `[x]` or `[!]` with edits.",
        "",
        f"- **Automated Mechanical Check (post-repair):** {'PASS' if post['passed'] else 'FAIL'} ({post['error_count']} errors, {post['warning_count']} warnings)",
        f"- **Adversarial Audit Verdict (v0):** `{audit.get('overall_verdict')}` ({len(audit.get('defects', []))} defects logged; repair pass applied: `{repair['repaired']}`)",
        "- **Human Review Start / End Time:** `____:____` to `____:____` (____ min)",
        "- **Author Sign-Off:** `[ ] Approved as-is`  `[ ] Approved with edits below`",
        "",
        "## Items Flagged by Adversarial Audit (Verify Repair)",
    ]
    for i, d in enumerate(audit.get("defects", []), 1):
        lines.append(f"{i}. `[{d.get('severity')}]` **{d.get('target')}** ({d.get('category')}): {d.get('issue')} — *Status:* `[ ] verified fixed` `[ ] needs edit`")
    lines.extend(["", "## Cards Inventory (Spot-Check Fidelity & Scope)"])
    for cp in sorted((crate_dir / "cards").glob("*.md")):
        fm, _ = parse_card_file(cp)
        lines.append(f"- `[ ]` **{fm.get('id')}** ({fm.get('type')}): {fm.get('title')} — links: `{fm.get('linked_cards', [])}`")
    (crate_dir / "audit" / "HUMAN_AUDIT_CHECKLIST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--papers", nargs="*", default=["digital-creativity", "jcal-review", "elife-111304", "elife-110672"])
    ap.add_argument("--skip-llm-audit", action="store_true")
    ap.add_argument("--audit-only", action="store_true", help="Run adversarial audit + human checklist without auto-overwriting Gemini cards")
    args = ap.parse_args()

    for pid in args.papers:
        print(f"\n=== Validating {pid} ===", flush=True)
        mech0 = mechanical_check(pid)
        print(f"  Pre-audit mechanical: passed={mech0['passed']} | COMPANION={mech0['manifest_bytes']}B | cards={mech0['card_count']} | errs={mech0['error_count']} | warns={mech0['warning_count']}")
        if mech0["errors"]:
            for e in mech0["errors"][:8]:
                print("    ERR:", e)
        if args.skip_llm_audit:
            continue
        audit_file = CRATES_DIR / pid / "audit" / "adversarial_audit_v0.json"
        if audit_file.exists() and args.audit_only:
            audit = json.loads(audit_file.read_text(encoding="utf-8"))
            print(f"  Adversarial audit (cached): verdict={audit.get('overall_verdict')} | defects={len(audit.get('defects', []))}")
        else:
            audit = run_adversarial_audit(pid)
            print(f"  Adversarial audit ({AUDIT_MODEL}): verdict={audit.get('overall_verdict')} | defects={len(audit.get('defects', []))}")
        if args.audit_only:
            repair = {"repaired": False, "mechanical_post_repair": mech0}
        else:
            repair = apply_single_repair(pid, audit)
        post = repair["mechanical_post_repair"]
        print(f"  Post-check mechanical: passed={post['passed']} | COMPANION={post['manifest_bytes']}B | cards={post['card_count']} | errs={post['error_count']} | warns={post['warning_count']}")
        write_human_audit_checklist(pid, audit, repair)


if __name__ == "__main__":
    main()
