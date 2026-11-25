# PDRP — Progressive-Disclosure Research Protocol

Reference implementation, deterministic RO-Crate validator, benchmark suite, and zero-dependency Model Context Protocol (MCP) server for:

> **The Progressive-Disclosure Research Protocol (PDRP): Designing Layered Context for AI-Assisted Academic Reading and Interrogation**  
> Atticus Sims (ORCID: [0009-0009-2933-2344](https://orcid.org/0009-0009-2933-2344)), University of Macau — Submitted to *Design Science* (Cambridge University Press / The Design Society).

## What PDRP Does
AI assistants reading academic articles face a three-way trade-off: main articles omit decisive supplementary protocols and caveats, preloading full supplementary bundles causes context dilution, and passive summaries trigger premature stopping (*compression substitution*). **PDRP** packages an immutable scholarly archive into three progressive-disclosure layers conforming to **RO-Crate 1.1 / 1.3**:

1. **Layer 0 (`COMPANION.md` <= 2.5 KB + `ro-crate-metadata.json`):** Compact entry manifest with an explicit **Negative-Coverage Map** declaring verified absences, a flat card directory, and SHA-256 checksums.
2. **Layer 1 (`cards/*.md`):** Atomic evidence cards (140–320 words) anchored to exact Layer-2 primary line ranges, with software-enforced bidirectional co-retrieval of linked Qualification/Update cards and deterministic `[VERIFY_PRIMARY_SPANS]` escalation cues.
3. **Layer 2 (`corpus/`):** Untouched primary article and supplementary archive accessed via calibrated Okapi BM25 search and bounded line reading.

## Try PDRP on This Paper in 30 Seconds
Zero API keys required (Python 3.10+ and `pyyaml` only):
```bash
pip install pyyaml
python examples/this_paper_design_science/tools/companion_reader.py validate
python examples/this_paper_design_science/tools/companion_reader.py manifest
python examples/this_paper_design_science/tools/companion_reader.py read-card C04
python examples/this_paper_design_science/tools/companion_reader.py search "unanswerable abstention"
```

## Mount as a Live MCP Server (`pdrp`)
Register inside Claude Desktop, Cursor, Windsurf, or Antigravity to let your AI assistant interrogate the paper using its own PDRP tools (`get_manifest`, `read_card`, `search_corpus`, `read_source`):
```json
{
  "mcpServers": {
    "pdrp": {
      "command": "python",
      "args": ["/absolute/path/to/pdrp/examples/this_paper_design_science/tools/companion_reader.py", "--mcp"]
    }
  }
}
```

## Repository Contents
- `tools/pdrp_server.py`: Standalone PDRP Cycle 2 retrieval engine, Okapi BM25 indexer, RO-Crate validator, and STDIO JSON-RPC 2.0 MCP server.
- `examples/this_paper_design_science/`: Mechanically validated self-referential PDRP companion for the *Design Science* article (`22/22` SHA-256 verified, `0` errors / `0` warnings).
- `examples/elife-111304/`: Companion crate for Liu, Jing *et al.* (2026, *eLife* 15:RP111304, CC-BY-4.0).
- `examples/elife-110672/`: Companion crate for Ohnezeit *et al.* (2026, *eLife* 15:RP110672, CC-BY-4.0).
- `benchmark_scripts/`: Evaluation harness, cross-family blinded scoring, reasoning toggle ablation, and human validation scoring scripts.

*(Note: The two unpublished internal manuscripts used strictly as zero-contamination internal benchmark cases are withheld until their respective journal publications; all open-access artifacts and full evaluation scripts are included here.)*

## Licensing
- Software and scripts: **MIT License** (`LICENSE-CODE`).
- Companion manifests, atomic evidence cards, and documentation: **CC-BY-4.0** (`LICENSE-ARTIFACTS`).
