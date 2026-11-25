"""Shared BM25 search + Progressive-Disclosure Card & Source Engine for Companion v3.

Exposes three clean tools to reader models:
  1. search_corpus(query, scope="all"|"companion"|"sources", top_k=8)
  2. read_source(source_id, start_line=1, end_line=120)
  3. read_card(card_id)   [Companion v3 only — automatically co-retrieves linked qualification/update cards!]
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

TOKEN_RE = re.compile(r"[a-z0-9]+(?:[._-][a-z0-9]+)*|[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    """Identifier-aware tokenizer: keeps both compound tokens (global_entropy, 0.7163) and subtokens."""
    low = text.lower()
    raw = TOKEN_RE.findall(low)
    out: list[str] = []
    for tok in raw:
        out.append(tok)
        if "_" in tok or "-" in tok:
            for part in re.split(r"[_-]+", tok):
                if part and part != tok:
                    out.append(part)
    return out


@dataclass
class Chunk:
    scope: str          # "sources" | "companion"
    doc_id: str         # source_id or card_id
    title: str
    start_line: int     # 1-based inclusive
    end_line: int       # 1-based inclusive
    text: str
    tokens: list[str]


class BM25Index:
    """Compact Okapi BM25 index over overlapping line-chunks with exact-phrase boost."""

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

    def search(self, query: str, allowed_scopes: set[str], top_k: int = 8) -> list[dict[str, Any]]:
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
            matched_terms = 0
            for t in set(q_tokens):
                f = tf.get(t, 0)
                if f == 0:
                    continue
                matched_terms += 1
                df = self.doc_freqs[t]
                idf = math.log(1.0 + (self.N - df + 0.5) / (df + 0.5))
                denom = f + self.k1 * (1.0 - self.b + self.b * dl / self.avgdl)
                score += idf * (f * (self.k1 + 1.0)) / denom
            if score <= 0:
                continue
            # Coverage bonus for multi-word queries + exact substring bonus
            if len(set(q_tokens)) > 1:
                score *= 1.0 + 0.35 * (matched_terms / len(set(q_tokens)))
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
            results.append(
                {
                    "scope": c.scope,
                    "id": c.doc_id,
                    "title": c.title,
                    "lines": f"{c.start_line}-{c.end_line}",
                    "score": round(sc, 3),
                    "snippet": snippet,
                }
            )
            if len(results) >= top_k:
                break
        return results


def parse_card_file(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            return fm, body
    return {}, raw.strip()


class PaperToolbox:
    """Encapsulates all read/search tools for one paper under a specific condition."""

    def __init__(self, corpus_dir: Path, crate_dir: Path | None, condition: str):
        self.corpus_dir = corpus_dir
        self.crate_dir = crate_dir
        self.condition = condition  # "paper_only" | "raw_supplements" | "companion_v3" | "companion_v3_1" | "naive_preload"
        self.metadata = json.loads((corpus_dir / "metadata.json").read_text(encoding="utf-8"))
        self.article_text = (corpus_dir / "article.txt").read_text(encoding="utf-8")
        self.article_lines = self.article_text.splitlines()
        self.article_aliases = {"article", "main_article", "article.txt", "s01", "jcal-s01"}

        self.sources: dict[str, tuple[dict[str, Any], list[str]]] = {}
        chunks: list[Chunk] = []

        # Load sources for all conditions with source access
        if condition in ("raw_supplements", "companion_v3", "companion_v3_1", "naive_preload"):
            for sm in self.metadata["sources"]:
                sid = sm["source_id"]
                sp = corpus_dir / sm["relpath"]
                if not sp.exists():
                    continue
                lines = sp.read_text(encoding="utf-8", errors="replace").splitlines()
                self.sources[sid] = (sm, lines)
                step = 10
                win = 16
                for start in range(0, max(1, len(lines)), step):
                    end = min(len(lines), start + win)
                    txt = "\n".join(lines[start:end])
                    if txt.strip():
                        chunks.append(
                            Chunk(
                                scope="sources",
                                doc_id=sid,
                                title=sm["title"],
                                start_line=start + 1,
                                end_line=end,
                                text=txt,
                                tokens=tokenize(sm["title"] + "\n" + txt),
                            )
                        )
                    if end >= len(lines):
                        break

        # Load companion cards if companion_v3, companion_v3_1, or naive_preload
        self.cards: dict[str, tuple[dict[str, Any], str, str]] = {}
        self.companion_manifest = ""
        if crate_dir and crate_dir.exists() and condition in ("companion_v3", "companion_v3_1", "naive_preload"):
            mp = crate_dir / "COMPANION.md"
            if mp.exists():
                self.companion_manifest = mp.read_text(encoding="utf-8")
            cards_dir = crate_dir / "cards"
            if cards_dir.exists():
                for cp in sorted(cards_dir.glob("*.md")):
                    fm, body = parse_card_file(cp)
                    cid = str(fm.get("id") or cp.stem).strip()
                    full_raw = cp.read_text(encoding="utf-8")
                    self.cards[cid] = (fm, body, full_raw)
                    title = str(fm.get("title", cid))
                    if condition in ("companion_v3", "companion_v3_1"):
                        chunks.append(
                            Chunk(
                                scope="companion",
                                doc_id=cid,
                                title=title,
                                start_line=1,
                                end_line=len(full_raw.splitlines()),
                                text=full_raw,
                                tokens=tokenize(cid + " " + title + "\n" + full_raw),
                            )
                        )

        self.index = BM25Index(chunks)

    def source_directory_summary(self) -> str:
        lines = []
        for sid, (sm, slines) in self.sources.items():
            lines.append(f"- `{sid}` ({sm['role']}, {len(slines)} lines): {sm['title']}")
        return "\n".join(lines)

    def full_preload_dump(self) -> str:
        parts = [self.companion_manifest.strip(), "\n\n=== ALL COMPANION CARDS ===\n"]
        for cid in sorted(self.cards):
            parts.append(f"\n--- CARD {cid} ---\n{self.cards[cid][2].strip()}")
        return "\n".join(parts)

    def openai_tool_schemas(self) -> list[dict[str, Any]]:
        if self.condition == "paper_only":
            return []
        is_comp = self.condition in ("companion_v3", "companion_v3_1")
        tools: list[dict[str, Any]] = [
            {
                "type": "function",
                "function": {
                    "name": "search_corpus",
                    "description": (
                        "BM25 keyword search over the paper's supplementary sources"
                        + (" and companion cards." if is_comp else ".")
                        + " Supports multi-word keyword queries (e.g. 'novelty 215 639', 'global_entropy NaN', 'reviewer control')."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Keywords or technical identifier to search."},
                            "scope": {
                                "type": "string",
                                "enum": ["all", "companion", "sources"] if is_comp else ["sources"],
                                "description": "Which files to search.",
                            },
                            "top_k": {"type": "integer", "minimum": 1, "maximum": 12, "description": "Max snippets (default 6)."},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_source",
                    "description": "Read exact numbered lines from a supplementary source file by its flat source_id (e.g. 'S03', 'author_response', 'jcal-s04', or 'article'). Max 200 lines per call.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_id": {"type": "string", "description": "Flat source_id from the source list, card pointers, or search results."},
                            "start_line": {"type": "integer", "minimum": 1, "description": "1-based start line (default 1)."},
                            "end_line": {"type": "integer", "minimum": 1, "description": "1-based inclusive end line (default start_line + 119)."},
                        },
                        "required": ["source_id"],
                    },
                },
            },
        ]
        if is_comp:
            card_desc = (
                "Read an atomic Knowledge Card by card_id from COMPANION.md (e.g. 'C01', 'M02', 'Q01'). "
                "Automatically includes any linked qualification, conflict, or post-publication update cards so limits are never missed."
            )
            if self.condition == "companion_v3_1":
                card_desc += (
                    " Also returns exact primary source-line pointers (`[VERIFY_PRIMARY_SPANS]`): "
                    "for short raw spans (<=80 lines, e.g. peer-review letters or compact tables), verify exact wording/values via `read_source` before answering."
                )
            tools.insert(
                0,
                {
                    "type": "function",
                    "function": {
                        "name": "read_card",
                        "description": card_desc,
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "card_id": {"type": "string", "description": "Card ID from COMPANION.md (e.g. 'C03')."},
                            },
                            "required": ["card_id"],
                        },
                    },
                },
            )
        return tools

    def _format_card_compact(self, cid: str) -> str:
        fm, body, _ = self.cards[cid]
        ctype = fm.get("type", "card")
        tstatus = fm.get("temporal_status", "")
        locs = fm.get("source_locators") or []
        loc_str = ", ".join(str(x) for x in locs)
        return f"=== CARD {cid} ({ctype} | temporal: {tstatus}) ===\nSources: {loc_str}\n\n{body.strip()}"

    def _build_verify_spans_footer(self, card_ids: list[str]) -> str:
        """Compute deterministic primary-source verification hints from card YAML source_locators."""
        seen: set[str] = set()
        short_spans: list[str] = []
        long_spans: list[str] = []
        for cid in card_ids:
            fm = self.cards[cid][0]
            for raw_loc in fm.get("source_locators") or []:
                loc = str(raw_loc).strip()
                if not loc or loc in seen:
                    continue
                seen.add(loc)
                m = re.match(r"^([^:\s]+):(\d+)(?:-(\d+))?$", loc)
                if not m:
                    continue
                sid = m.group(1)
                if sid.lower() in self.article_aliases:
                    continue
                s0 = int(m.group(2))
                s1 = int(m.group(3) or s0)
                span_len = max(1, s1 - s0 + 1)
                total_len = len(self.sources[sid][1]) if sid in self.sources else None
                entry = f"{sid}:{s0}-{s1} ({span_len}L" + (f" of {total_len}L" if total_len else "") + ")"
                if span_len <= 80:
                    short_spans.append(entry)
                else:
                    long_spans.append(entry)
        lines: list[str] = []
        if short_spans:
            lines.append(
                "[VERIFY_PRIMARY_SPANS (SHORT <=80L — call read_source if exact wording, peer-review framing, or table cells matter): "
                + "; ".join(short_spans[:10])
                + "]"
            )
        if long_spans:
            lines.append("[OTHER_PRIMARY_SPANS (>80L): " + "; ".join(long_spans[:6]) + "]")
        return "\n".join(lines)

    def execute(self, name: str, args: dict[str, Any], seen_cards: set[str] | None = None) -> str:
        if name == "read_card" and self.condition in ("companion_v3", "companion_v3_1"):
            cid = str(args.get("card_id", "")).strip()
            # Flexible case-insensitive lookup
            match = None
            for k in self.cards:
                if k.lower() == cid.lower():
                    match = k
                    break
            if not match:
                return json.dumps({"error": f"Unknown card_id '{cid}'. Available: {sorted(self.cards.keys())}"})
            fm, _, raw = self.cards[match]
            linked: list[str] = []

            def add_link(x: str) -> None:
                if not x:
                    return
                for k in self.cards:
                    if k.lower() == str(x).lower() and k != match and k not in linked:
                        linked.append(k)
                        return

            # 1. Highest priority: reverse-linked Q/U cards that qualify/conflict/update THIS card
            for other_id, (ofm, _, _) in self.cards.items():
                if other_id == match:
                    continue
                for rel in ofm.get("relations") or []:
                    if isinstance(rel, dict) and rel.get("type") in ("qualifies", "conflicts_with", "updates") and str(rel.get("target", "")).lower() == match.lower():
                        add_link(other_id)
            # 2. Explicit linked_cards (prioritizing Q and U cards first)
            raw_linked = fm.get("linked_cards") or []
            if isinstance(raw_linked, str):
                raw_linked = [raw_linked]
            for x in raw_linked:
                if str(x).upper().startswith(("Q", "U")):
                    add_link(str(x))
            # 3. Forward qualifies/conflicts_with/updates relations
            for rel in fm.get("relations") or []:
                if isinstance(rel, dict) and rel.get("type") in ("qualifies", "conflicts_with", "updates"):
                    add_link(str(rel.get("target", "")))
            # 4. Remaining explicit linked_cards (if space remains)
            for x in raw_linked:
                add_link(str(x))

            is_v31 = self.condition == "companion_v3_1"
            max_co = 2 if is_v31 else 3
            parts = [self._format_card_compact(match) if is_v31 else f"=== CARD {match} ===\n{raw.strip()}"]
            if seen_cards is not None:
                seen_cards.add(match)
            co_retrieved: list[str] = []
            already_shown: list[str] = []
            for lid in linked:
                if len(co_retrieved) >= max_co:
                    break
                if seen_cards is not None and lid in seen_cards:
                    already_shown.append(lid)
                    continue
                if is_v31:
                    parts.append("\n[AUTO-LINKED QUALIFICATION / UPDATE]\n" + self._format_card_compact(lid))
                else:
                    parts.append(f"\n=== AUTO-LINKED QUALIFICATION / UPDATE CARD {lid} ===\n{self.cards[lid][2].strip()}")
                co_retrieved.append(lid)
                if seen_cards is not None:
                    seen_cards.add(lid)
            footer = f"\n\n[co_retrieved_cards: {co_retrieved}]"
            if already_shown:
                footer += f"\n[already_shown_in_session: {already_shown}]"
            if is_v31:
                vfooter = self._build_verify_spans_footer([match] + co_retrieved)
                if vfooter:
                    footer += "\n" + vfooter
            return "\n".join(parts) + footer

        if name == "search_corpus":
            q = str(args.get("query", "")).strip()
            scope = str(args.get("scope", "all")).strip().lower()
            top_k = max(1, min(int(args.get("top_k", 6) or 6), 12))
            if self.condition in ("companion_v3", "companion_v3_1"):
                if scope == "companion":
                    allowed = {"companion"}
                elif scope in ("sources", "source", "supplementary", "supplements"):
                    allowed = {"sources"}
                else:
                    # Normalize 'all' or any model-invented scope (e.g. 'article', 'jcal-s01') safely
                    allowed = {"companion", "sources"}
            else:
                allowed = {"sources"}
            hits = self.index.search(q, allowed_scopes=allowed, top_k=top_k)
            if not hits:
                return json.dumps(
                    {
                        "query": q,
                        "scope": sorted(allowed),
                        "hits": [],
                        "note": "No matches found in searched scope. Try broader or single-word terms; zero hits does not prove absence from unsearched files.",
                    },
                    indent=2,
                )
            return json.dumps({"query": q, "scope": sorted(allowed), "hits": hits}, indent=2)

        if name == "read_source":
            sid = str(args.get("source_id", "")).strip()
            if sid.lower() in self.article_aliases:
                lines = self.article_lines
                total = len(lines)
                start = max(1, int(args.get("start_line", 1) or 1))
                end = int(args.get("end_line", start + 119) or (start + 119))
                end = min(total, max(start, min(end, start + 199)))
                numbered = [f"{i}: {lines[i - 1]}" for i in range(start, end + 1)]
                return (
                    f"=== SOURCE article ({self.metadata['title']}) | lines {start}-{end} of {total} ===\n"
                    + "\n".join(numbered)
                )
            match = None
            for k in self.sources:
                if k.lower() == sid.lower() or self.sources[k][0]["filename"].lower() == sid.lower():
                    match = k
                    break
            if not match:
                return json.dumps({"error": f"Unknown source_id '{sid}'. Use 'article' or one of: {sorted(self.sources.keys())[:30]}"})
            sm, lines = self.sources[match]
            total = len(lines)
            start = max(1, int(args.get("start_line", 1) or 1))
            end = int(args.get("end_line", start + 119) or (start + 119))
            end = min(total, max(start, min(end, start + 199)))
            numbered = [f"{i}: {lines[i - 1]}" for i in range(start, end + 1)]
            return (
                f"=== SOURCE {match} ({sm['title']}) | lines {start}-{end} of {total} ===\n"
                + "\n".join(numbered)
            )

        return json.dumps({"error": f"Unsupported tool '{name}' in condition '{self.condition}'."})
