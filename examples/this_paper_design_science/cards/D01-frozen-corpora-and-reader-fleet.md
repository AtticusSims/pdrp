---
id: D01
title: Specifications of the four multidisciplinary frozen archives and eight-model
  cloud/local reader fleet
type: data
temporal_status: current
source_locators:
- article:134-157
- supplement_s1:20-30
- supplement_s1:70-87
relations:
- type: supports
  target: M02
  basis: Exact archive sizes, card counts, providers, and GPU runtime limits
linked_cards:
- M02
- Q02
- C03
---

# D01: Specifications of the four multidisciplinary frozen archives and eight-model cloud/local reader fleet

The four frozen benchmark corpora span an order-of-magnitude archive gradient (Table 3, article:134-141; case-to-archive key in supplement_s1:20-30): (1) Computational Aesthetics (digital-creativity): empirical computational-design manuscript, 51.4 KB article, 60 supplementary files (1.08 MB), 2,343 B manifest, 18 cards; (2) Creative-Coding Review (jcal-review): qualitative narrative review, 104.9 KB article, 8 files (181 KB), 2,294 B manifest, 16 cards; (3) Hippocampal Ripples (elife-111304, Liu, Jing et al. 2026 VOR, 20 Nov 2026): human intracranial electrophysiology, 82.6 KB article, 5 files (125 KB), 2,319 B manifest, 16 cards; and (4) Nanopore RNA Calibration (elife-110672, Ohnezeit et al. 2026 VOR, 20 Nov 2026): direct RNA m6A sequencing, 97.5 KB article, 8 files incl. compact CSVs (37 KB), 2,280 B manifest, 18 cards. Total companion corpus: 68 atomic cards, manifests 2,280-2,343 B. Eight reader models spanned six families (all capped at 8 turns and 8,192 output tokens; supplement_s1:70-85): five OpenRouter cloud endpoints (qwen/qwen3.8-max-0902, mistralai/mistral-large-4-0, open-weight thinkingmachines/inkling-2-small, and x-ai/grok-4.6 with mandatory native reasoning ON [HTTP 400 if disabled]; plus deepseek/deepseek-v3.2 defaulting to reasoning OFF, toggled ON in ablation) and three local open-weight models running 100% GPU-resident on one NVIDIA RTX 5090 (32 GB VRAM, Ollama 0.40.16 native /api/chat): qwen3.8:27b-q4_K_M (ON 49,152 ctx -> OFF 40,960 ctx), gemma4:31b-it-qat (ON 40,960 ctx; OOM on explicit toggle), and gpt-oss:20b (Med -> Low at 49,152 ctx).
