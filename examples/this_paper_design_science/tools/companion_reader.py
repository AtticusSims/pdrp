#!/usr/bin/env python3
"""Self-Contained Progressive-Disclosure Research Companion (v3.1) Engine, Validator & MCP Server.

Allows peer reviewers, editors, and readers to interrogate this Design Science manuscript
using the exact Cycle 2 (v3.1) progressive-disclosure protocol introduced and evaluated in the article:
  - Layer 0: Compact Entry Manifest (COMPANION.md <= 2.5 KB) with explicit Negative-Coverage Map
  - Layer 1: Atomic Evidence Cards with software-enforced bidirectional qualification co-retrieval (top-2 Q/U)
             and deterministic [VERIFY_PRIMARY_SPANS] short-span escalation footers (<= 80 lines)
  - Layer 2: Frozen Primary Archive accessed via calibrated Okapi BM25 (k1=1.5, b=0.75) and bounded line reads

Zero external API keys or paid services required (Python 3.10+ standard library + PyYAML).

Usage:
  python tools/companion_reader.py validate
  python tools/companion_reader.py manifest
  python tools/companion_reader.py read-card C04
  python tools/companion_reader.py search "Frontier-4 Judge A ceiling"
  python tools/companion_reader.py read-source supplement_s1 180 194
  python tools/companion_reader.py --mcp        # STDIO JSON-RPC 2.0 Model Context Protocol server
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CRATE_ROOT = Path(__file__).resolve().parent.parent
CORPUS_DIR = CRATE_ROOT / "corpus"
CARDS_DIR = CRATE_ROOT / "cards"

ALLOWED_RELATIONS = {"supports", "qualifies", "derived_from", "uses", "conflicts_with", "responds_to", "updates"}
ALLOWED_TYPES = {"claim", "method", "data", "qualification", "review_disposition", "update"}
MAX_MANIFEST_BYTES = 2500
TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)*|[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    low = text.lower()
    out: list[str] = []
    for tok in TOKEN_RE.findall(low):
        out.append(tok)
        if "_" in tok or "-" in tok:
            for part in re.split(r"[_-]+", tok):
                if part and part != tok:
                    out.append(part)
    return out


@dataclass
class Chunk:
    scope: str
    doc_id: str
    title: str
    start_line: int
    end_line: int
    text: str
    tokens: list[str]


class BM25Index:
    """Calibrated Okapi BM25 index over overlapping line windows with exact-phrase boost."""

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.N = len(chunks)
        self.avgdl = (sum(len(c.tokens) for c in chunks) / self.N) if self.N else 1.0
        self.doc_freqs: Counter[str] = Counter()
        self.term_counts: list[Counter[str]] = []
        for c in chunks:
            tf = Counter(c.tokens)
            self.term_counts.append(tf)
            for term in tf:
                self.doc_freqs[term] += 1

    def search(self, query: str, allowed_scopes: set[str], top_k: int = 6) -> list[dict[str, Any]]:
        q_tokens = tokenize(query)
        if not q_tokens:
            return []
        q_low = query.strip().lower()
        scores: list[tuple[float, int]] = []
        for idx, c in enumerate(self.chunks):
            if c.scope not in allowed_scopes:
                continue
            tf = self.term_counts[idx]
            dl = len(c.tokens) or 1
            score = 0.0
            matched = 0
            for t in set(q_tokens):
                f = tf.get(t, 0)
                if f == 0:
                    continue
                matched += 1
                df = self.doc_freqs[t]
                idf = math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))
                denom = f + self.k1 * (1.0 - self.b + self.b * dl / self.avgdl)
                score += idf * (f * (self.k1 + 1.0)) / denom
            if score <= 0:
                continue
            if len(set(q_tokens)) > 1:
                score *= 1.0 + 0.35 * (matched / len(set(q_tokens)))
            if len(q_low) >= 4 and q_low in c.text.lower():
                score *= 1.4
            scores.append((score, idx))

        scores.sort(key=lambda x: -x[0])
        results: list[dict[str, Any]] = []
        seen_windows: set[tuple[str, str, int]] = set()
        for sc, idx in scores:
            c = self.chunks[idx]
            bucket = (c.scope, c.doc_id, c.start_line // 12)
            if bucket in seen_windows:
                continue
            seen_windows.add(bucket)
            snippet = c.text.strip()
            if len(snippet) > 900:
                snippet = snippet[:900] + "\n...[truncated; call read_source/read_card for full lines]"
            results.append({
                "scope": c.scope,
                "id": c.doc_id,
                "title": c.title,
                "lines": f"{c.start_line}-{c.end_line}",
                "score": round(sc, 3),
                "snippet": snippet,
            })
            if len(results) >= top_k:
                break
        return results


def parse_card_file(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            return yaml.safe_load(parts[1]) or {}, parts[2].strip()
    return {}, raw.strip()


class CompanionV31Engine:
    """Exact Cycle 2 (v3.1) progressive-disclosure engine over this crate."""

    def __init__(self, crate_root: Path = CRATE_ROOT):
        self.crate_root = crate_root
        self.corpus_dir = crate_root / "corpus"
        self.cards_dir = crate_root / "cards"
        self.metadata = json.loads((self.corpus_dir / "metadata.json").read_text(encoding="utf-8"))
        self.manifest_text = (crate_root / "COMPANION.md").read_text(encoding="utf-8")
        self.article_lines = (self.corpus_dir / "article.txt").read_text(encoding="utf-8").splitlines()
        self.article_aliases = {"article", "main_article", "article.txt", "manuscript"}

        self.sources: dict[str, tuple[dict[str, Any], list[str]]] = {}
        chunks: list[Chunk] = []

        # Index article and all supplementary sources
        def add_source_chunks(doc_id: str, title: str, lines: list[str]) -> None:
            for start in range(0, max(1, len(lines)), 10):
                end = min(len(lines), start + 16)
                txt = "\n".join(lines[start:end])
                if txt.strip():
                    chunks.append(Chunk("sources", doc_id, title, start + 1, end, txt, tokenize(title + "\n" + txt)))
                if end >= len(lines):
                    break

        add_source_chunks("article", self.metadata["title"], self.article_lines)
        for sm in self.metadata["sources"]:
            sid = sm["source_id"]
            sp = self.corpus_dir / sm["relpath"]
            if sp.exists():
                lines = sp.read_text(encoding="utf-8", errors="replace").splitlines()
                self.sources[sid] = (sm, lines)
                add_source_chunks(sid, sm["title"], lines)

        self.cards: dict[str, tuple[dict[str, Any], str, str]] = {}
        for cp in sorted(self.cards_dir.glob("*.md")):
            fm, body = parse_card_file(cp)
            cid = str(fm.get("id") or cp.stem).strip()
            full_raw = cp.read_text(encoding="utf-8")
            self.cards[cid] = (fm, body, full_raw)
            title = str(fm.get("title", cid))
            chunks.append(Chunk("companion", cid, title, 1, len(full_raw.splitlines()), full_raw, tokenize(cid + " " + title + "\n" + full_raw)))

        self.index = BM25Index(chunks)

    def _format_card_compact(self, cid: str) -> str:
        fm, body, _ = self.cards[cid]
        locs = ", ".join(str(x) for x in (fm.get("source_locators") or []))
        return f"=== CARD {cid} ({fm.get('type', 'card')} | temporal: {fm.get('temporal_status', '')}) ===\nSources: {locs}\n\n{body.strip()}"

    def _verify_spans_footer(self, card_ids: list[str]) -> str:
        seen: set[str] = set()
        short_spans: list[str] = []
        long_spans: list[str] = []
        for cid in card_ids:
            for raw_loc in (self.cards[cid][0].get("source_locators") or []):
                loc = str(raw_loc).strip()
                if not loc or loc in seen:
                    continue
                seen.add(loc)
                m = re.match(r"^([^:\s]+):(\d+)(?:-(\d+))?$", loc)
                if not m:
                    continue
                sid, s0, s1 = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
                if sid.lower() in self.article_aliases:
                    continue
                span_len = max(1, s1 - s0 + 1)
                total_len = len(self.sources[sid][1]) if sid in self.sources else None
                entry = f"{sid}:{s0}-{s1} ({span_len}L" + (f" of {total_len}L" if total_len else "") + ")"
                (short_spans if span_len <= 80 else long_spans).append(entry)
        lines: list[str] = []
        if short_spans:
            lines.append("[VERIFY_PRIMARY_SPANS (SHORT <=80L — call read_source if exact wording or table cells matter): " + "; ".join(short_spans[:10]) + "]")
        if long_spans:
            lines.append("[OTHER_PRIMARY_SPANS (>80L): " + "; ".join(long_spans[:6]) + "]")
        return "\n".join(lines)

    def read_card(self, card_id: str) -> str:
        match = next((k for k in self.cards if k.lower() == card_id.strip().lower()), None)
        if not match:
            return json.dumps({"error": f"Unknown card_id '{card_id}'. Available: {sorted(self.cards)}"})
        fm = self.cards[match][0]
        linked: list[str] = []

        def add_link(x: str) -> None:
            for k in self.cards:
                if k.lower() == str(x).lower() and k != match and k not in linked:
                    linked.append(k)
                    return

        # 1. Reverse inbound qualifies / conflicts_with / updates (forcing function)
        for other_id, (ofm, _, _) in self.cards.items():
            if other_id == match:
                continue
            for rel in ofm.get("relations") or []:
                if isinstance(rel, dict) and rel.get("type") in ("qualifies", "conflicts_with", "updates") and str(rel.get("target", "")).lower() == match.lower():
                    add_link(other_id)
        # 2. Explicit Q/U linked_cards
        for x in (fm.get("linked_cards") or []):
            if str(x).upper().startswith(("Q", "U")):
                add_link(str(x))
        # 3. Forward qualifies / conflicts_with / updates
        for rel in fm.get("relations") or []:
            if isinstance(rel, dict) and rel.get("type") in ("qualifies", "conflicts_with", "updates"):
                add_link(str(rel.get("target", "")))
        # 4. Remaining explicit linked_cards
        for x in (fm.get("linked_cards") or []):
            add_link(str(x))

        parts = [self._format_card_compact(match)]
        co_retrieved: list[str] = []
        for lid in linked[:2]:  # Cycle 2 (v3.1) top-2 co-retrieval cap
            parts.append("\n[AUTO-LINKED QUALIFICATION / UPDATE]\n" + self._format_card_compact(lid))
            co_retrieved.append(lid)
        footer = f"\n\n[co_retrieved_cards: {co_retrieved}]"
        vfooter = self._verify_spans_footer([match] + co_retrieved)
        if vfooter:
            footer += "\n" + vfooter
        return "\n".join(parts) + footer

    def search_corpus(self, query: str, scope: str = "all", top_k: int = 6) -> str:
        sc = scope.strip().lower()
        if sc == "companion":
            allowed = {"companion"}
        elif sc in ("sources", "source", "supplementary", "supplements"):
            allowed = {"sources"}
        else:
            allowed = {"companion", "sources"}
        hits = self.index.search(query, allowed_scopes=allowed, top_k=max(1, min(int(top_k), 12)))
        return json.dumps({"query": query, "scope": sorted(allowed), "hits": hits}, indent=2)

    def read_source(self, source_id: str, start_line: int = 1, end_line: int | None = None) -> str:
        sid = source_id.strip()
        if sid.lower() in self.article_aliases:
            lines = self.article_lines
            title = self.metadata["title"]
            label = "article"
        else:
            match = next((k for k in self.sources if k.lower() == sid.lower() or self.sources[k][0]["filename"].lower() == sid.lower()), None)
            if not match:
                return json.dumps({"error": f"Unknown source_id '{sid}'. Use 'article' or one of: {sorted(self.sources)}"})
            sm, lines = self.sources[match]
            title, label = sm["title"], match
        total = len(lines)
        start = max(1, int(start_line or 1))
        end = min(total, max(start, min(int(end_line or (start + 119)), start + 199)))
        body = "\n".join(f"{i}: {lines[i - 1]}" for i in range(start, end + 1))
        return f"=== SOURCE {label} ({title}) | lines {start}-{end} of {total} ===\n{body}"


def validate_crate(crate_root: Path = CRATE_ROOT) -> dict[str, Any]:
    """Deterministic mechanical validator matching benchmark scripts/03_validate_crates.py."""
    meta = json.loads((crate_root / "corpus" / "metadata.json").read_text(encoding="utf-8"))
    line_limits = {"article": meta["article"]["lines"]}
    for sm in meta["sources"]:
        line_limits[sm["source_id"]] = sm["lines"]

    errors: list[str] = []
    warnings: list[str] = []

    mp = crate_root / "COMPANION.md"
    m_bytes = mp.stat().st_size if mp.exists() else 0
    m_text = mp.read_text(encoding="utf-8") if mp.exists() else ""
    if not mp.exists():
        errors.append("Missing COMPANION.md")
    elif m_bytes > MAX_MANIFEST_BYTES:
        errors.append(f"COMPANION.md exceeds {MAX_MANIFEST_BYTES} B ({m_bytes} B)")

    # RO-Crate JSON-LD & SHA-256 verification
    rc_path = crate_root / "ro-crate-metadata.json"
    verified_hashes = 0
    if not rc_path.exists():
        errors.append("Missing ro-crate-metadata.json")
    else:
        rc = json.loads(rc_path.read_text(encoding="utf-8"))
        if "@context" not in rc or "@graph" not in rc:
            errors.append("ro-crate-metadata.json missing @context or @graph")
        for node in rc.get("@graph", []):
            if node.get("@type") == "File" and "sha256" in node:
                fp = crate_root / node["@id"]
                if not fp.exists():
                    errors.append(f"RO-Crate references missing file: {node['@id']}")
                else:
                    actual = hashlib.sha256(fp.read_bytes()).hexdigest()
                    if actual != node["sha256"]:
                        errors.append(f"SHA-256 mismatch on {node['@id']}")
                    else:
                        verified_hashes += 1

    cards: dict[str, tuple[dict[str, Any], str]] = {}
    for cp in sorted((crate_root / "cards").glob("*.md")):
        fm, body = parse_card_file(cp)
        cid = str(fm.get("id", "")).strip()
        if not cid:
            errors.append(f"{cp.name}: missing id")
            continue
        cards[cid] = (fm, body)
        if str(fm.get("type", "")) not in ALLOWED_TYPES:
            warnings.append(f"{cid}: non-standard type")
        wc = len(body.split())
        if wc < 80 or wc > 420:
            warnings.append(f"{cid}: body word count {wc} outside [80, 420]")
        locs = fm.get("source_locators") or []
        if not locs:
            errors.append(f"{cid}: empty source_locators")
        for loc in locs:
            m = re.match(r"^([A-Za-z0-9_.-]+):(\d+)(?:-(\d+))?$", str(loc).strip())
            if not m:
                warnings.append(f"{cid}: bad locator format '{loc}'")
                continue
            sid, s0, s1 = m.group(1), int(m.group(2)), int(m.group(3) or m.group(2))
            if sid not in line_limits:
                errors.append(f"{cid}: unknown source_id '{sid}'")
            elif s0 < 1 or s1 < s0 or s1 > line_limits[sid]:
                errors.append(f"{cid}: line range '{loc}' exceeds {sid} max {line_limits[sid]}")
        for rel in fm.get("relations") or []:
            if isinstance(rel, dict) and rel.get("type") not in ALLOWED_RELATIONS:
                errors.append(f"{cid}: disallowed relation '{rel.get('type')}'")

    for cid, (fm, _) in cards.items():
        if cid not in m_text:
            errors.append(f"{cid}: missing from COMPANION.md")
        for lid in fm.get("linked_cards") or []:
            if str(lid) not in cards:
                errors.append(f"{cid}: broken linked_cards target '{lid}'")
        for rel in fm.get("relations") or []:
            if isinstance(rel, dict) and str(rel.get("target", "")) not in cards:
                errors.append(f"{cid}: broken relation target '{rel.get('target')}'")

    return {
        "crate": meta["paper_id"],
        "passed": len(errors) == 0,
        "manifest_bytes": m_bytes,
        "manifest_cap_bytes": MAX_MANIFEST_BYTES,
        "card_count": len(cards),
        "verified_sha256_files": verified_hashes,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def serve_mcp(engine: CompanionV31Engine) -> None:
    """Minimal zero-dependency STDIO JSON-RPC 2.0 Model Context Protocol (MCP) server."""
    tools_spec = [
        {
            "name": "get_manifest",
            "description": "Return Layer-0 COMPANION.md (<2.5 KB) with Coverage Map, Negative-Coverage Map, and flat 15-card index.",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "read_card",
            "description": "Read an atomic Layer-1 evidence card (e.g., C04, M01, Q01). Automatically bundles up to 2 linked Qualification/Update cards and appends [VERIFY_PRIMARY_SPANS] short-span escalation hints.",
            "inputSchema": {"type": "object", "properties": {"card_id": {"type": "string"}}, "required": ["card_id"]},
        },
        {
            "name": "search_corpus",
            "description": "Calibrated Okapi BM25 search (k1=1.5, b=0.75) across the frozen manuscript, supplementary reports, and companion cards.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "scope": {"type": "string", "enum": ["all", "companion", "sources"], "default": "all"},
                    "top_k": {"type": "integer", "default": 6},
                },
                "required": ["query"],
            },
        },
        {
            "name": "read_source",
            "description": "Read exact numbered lines from the frozen manuscript ('article') or any Layer-2 supplementary record (e.g., 'supplement_s1', 'human_validation_report', 'reasoning_ablation_report').",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source_id": {"type": "string"},
                    "start_line": {"type": "integer", "default": 1},
                    "end_line": {"type": "integer"},
                },
                "required": ["source_id"],
            },
        },
    ]

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        req = json.loads(raw_line)
        req_id = req.get("id")
        method = req.get("method", "")
        params = req.get("params") or {}

        if method == "initialize":
            res: Any = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "pdrp", "version": "3.1.0"},
            }
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            res = {"tools": tools_spec}
        elif method == "tools/call":
            tname = params.get("name", "")
            targs = params.get("arguments") or {}
            if tname == "get_manifest":
                txt = engine.manifest_text
            elif tname == "read_card":
                txt = engine.read_card(str(targs.get("card_id", "")))
            elif tname == "search_corpus":
                txt = engine.search_corpus(str(targs.get("query", "")), str(targs.get("scope", "all")), int(targs.get("top_k", 6)))
            elif tname == "read_source":
                txt = engine.read_source(str(targs.get("source_id", "")), int(targs.get("start_line", 1)), targs.get("end_line"))
            else:
                txt = json.dumps({"error": f"Unknown tool '{tname}'"})
            res = {"content": [{"type": "text", "text": txt}]}
        else:
            res = {}

        if req_id is not None:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": res}) + "\n")
            sys.stdout.flush()


def main() -> None:
    ap = argparse.ArgumentParser(description="Progressive-Disclosure Research Companion (v3.1) CLI & MCP Server")
    ap.add_argument("--mcp", action="store_true", help="Run as STDIO Model Context Protocol (MCP) server")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("validate", help="Run deterministic RO-Crate, SHA-256, locator, and link-closure checks")
    sub.add_parser("manifest", help="Print Layer-0 COMPANION.md entry manifest")
    rc_p = sub.add_parser("read-card", help="Read a Layer-1 card with automatic top-2 Q/U co-retrieval")
    rc_p.add_argument("card_id")
    sc_p = sub.add_parser("search", help="Run calibrated Okapi BM25 search")
    sc_p.add_argument("query")
    sc_p.add_argument("--scope", default="all", choices=["all", "companion", "sources"])
    sc_p.add_argument("--top-k", type=int, default=6)
    rs_p = sub.add_parser("read-source", help="Read exact numbered lines from article or Layer-2 source")
    rs_p.add_argument("source_id")
    rs_p.add_argument("start_line", type=int, nargs="?", default=1)
    rs_p.add_argument("end_line", type=int, nargs="?", default=None)

    args = ap.parse_args()
    if args.cmd == "validate":
        report = validate_crate(CRATE_ROOT)
        print(json.dumps(report, indent=2))
        sys.exit(0 if report["passed"] else 1)

    engine = CompanionV31Engine(CRATE_ROOT)
    if args.mcp:
        serve_mcp(engine)
        return
    if args.cmd == "manifest":
        print(engine.manifest_text)
    elif args.cmd == "read-card":
        print(engine.read_card(args.card_id))
    elif args.cmd == "search":
        print(engine.search_corpus(args.query, args.scope, args.top_k))
    elif args.cmd == "read-source":
        print(engine.read_source(args.source_id, args.start_line, args.end_line))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
