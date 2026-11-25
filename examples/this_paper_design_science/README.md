# Online Supplement S2: Self-Referential PDRP Research Companion

**Companion Crate for:** *The Progressive-Disclosure Research Protocol (PDRP): Designing Layered Context for AI-Assisted Academic Reading and Interrogation* (*Design Science* Research Article)  
**Author:** Atticus Sims (ORCID: 0009-0009-2933-2344)  
**License:** Code MIT / Companion Artifacts CC-BY-4.0

This folder packages *this manuscript itself* using the exact **Cycle 2 (`v3.1`) Progressive-Disclosure Research Protocol (PDRP)** introduced and evaluated in the article, so peer reviewers, editors, and readers can directly experience and audit the protocol on the paper's own frozen empirical evidence.

## Package Layout (RO-Crate 1.1 / 1.3 Compatible)

- **Layer 0 (`COMPANION.md` + `ro-crate-metadata.json`):** Compact entry manifest (strictly ≤ 2,500 B cap) with an explicit Negative-Coverage Map, flat 15-card directory, and SHA-256 checksums across all 22 packaged files.
- **Layer 1 (`cards/*.md`):** 15 atomic evidence cards (`C01–C05`, `M01–M03`, `D01–D02`, `Q01–Q04`, `U01`; 185–265 words each) anchored to exact primary line ranges with typed bidirectional relations.
- **Layer 2 (`corpus/`):** Frozen untouched snapshots of the manuscript (`article.txt`) and four primary supplementary study records (`supplement_s1`, `human_validation_report`, `reasoning_ablation_report`, `results_report`).
- **Runnable Tool Engine & MCP Server (`tools/companion_reader.py`):** Self-contained Python 3.10+ script (`pyyaml` + stdlib only; zero paid API keys required) implementing exact PDRP Cycle 2 retrieval (`read_card` with software-enforced top-2 bidirectional `Q`/`U` co-retrieval and `[VERIFY_PRIMARY_SPANS]` footers, calibrated Okapi BM25 `search_corpus`, bounded `read_source`, deterministic validator, and a zero-dependency STDIO JSON-RPC 2.0 Model Context Protocol server).

## Quick-Start for Reviewers

### 1. Verify RO-Crate Integrity & SHA-256 Checksums
```bash
python tools/companion_reader.py validate
```

### 2. Inspect Layer-0 Manifest, Cards (With Automatic Caveat Bundling), and Primary Spans
```bash
# View Layer-0 entry manifest and Negative-Coverage Map
python tools/companion_reader.py manifest

# Read Claim C04 — automatically co-retrieves Q01 (single-judge ceiling) and Q04 (role-overlap & DP4 gap)
python tools/companion_reader.py read-card C04

# Read Claim C05 — automatically co-retrieves Q02 (Qwen 40K GPU cap & inversion) and U01 (Cycle 1->2 redesign)
python tools/companion_reader.py read-card C05

# Run calibrated Okapi BM25 search over frozen primary sources and cards
python tools/companion_reader.py search "Frontier-4 Judge A ceiling"

# Escalate to exact verified lines in Layer 2
python tools/companion_reader.py read-source supplement_s1 180 195
```

### 3. Connect as a Live Model Context Protocol (MCP) Server (`pdrp`)
Add the following entry to any MCP-compatible AI client (Claude Desktop, Cursor, Windsurf, or Antigravity) to let your AI assistant interrogate this manuscript using its own PDRP tools (`get_manifest`, `read_card`, `search_corpus`, `read_source`):

```json
{
  "mcpServers": {
    "pdrp": {
      "command": "python",
      "args": ["/absolute/path/to/self_companion_crate/tools/companion_reader.py", "--mcp"]
    }
  }
}
```
