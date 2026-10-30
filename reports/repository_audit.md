# Repository Audit Report

**Audited:** 2026-10-30  
**Auditor:** Antigravity AI (autonomous audit — all findings from direct file inspection)

---

## 1. Repository Structure

```
Evaluating Multilingual Reliability of Large Language Models/
├── configs/
│   └── experiment.yaml          # Frozen experiment settings
├── data/
│   └── hindi_queries_template.csv   # Schema only — no data rows
├── paper/
│   └── paper_outline.md         # Manuscript scaffold (no results filled)
├── prompts/
│   ├── antigravity_master_prompt.txt  # 8-stage work order for AI assistant
│   └── README.md                # 18-prompt staged workflow guide
├── results/                     # EMPTY — no experiment outputs yet
├── scripts/
│   └── run_retrieval.py         # Main retrieval and evaluation script
├── .gitignore
├── ai_assistance_log.md         # Template only — no entries
├── baseline_validation.md       # Template only — all checks UNKNOWN
├── README.md                    # Detailed project guide
├── requirements.txt             # 8 Python dependencies
└── research_decisions.md        # Decisions log — proposals, not verified
```

---

## 2. What Is Already Implemented (VERIFIED by inspection)

### Source Code
- `scripts/run_retrieval.py` (154 lines): A complete, well-structured retrieval pipeline implementing:
  - BM25 via `rank_bm25.BM25Okapi` with whitespace/lowercase tokenizer
  - Dense retrieval via `sentence_transformers.SentenceTransformer` for two models
  - BEIR dataset loading via `beir.datasets.data_loader.GenericDataLoader`
  - Automatic SciFact dataset download from official UKP/TU Darmstadt URL
  - Recall@1, Recall@5, Recall@10, MRR@10 computation
  - Query-level and aggregate metric serialization (CSV + JSON)
  - Failure case extraction (queries with MRR@10 == 0)
  - `--limit_queries` flag for smoke testing
  - `--languages en,hi` flag for bilingual runs
  - `--hindi_csv` flag with schema validation and human-check warnings
  - Seed 42 fixed for reproducibility

### Configuration
- `configs/experiment.yaml`: All experiment parameters frozen (seed, dataset, split, languages, top_k, methods, primary metric, translation policy).

### Documentation Scaffolds
- `README.md`: Complete usage instructions.
- `research_decisions.md`: 3 decisions recorded (scope, comparators, metrics).
- `paper/paper_outline.md`: 11-section outline (no results filled).
- `baseline_validation.md`: Template with 11 validation checks.
- `ai_assistance_log.md`: Template with logging schema.

### Data Schema
- `data/hindi_queries_template.csv`: Header only — defines required columns: `query_id`, `english_text`, `hindi_text`, `translation_method`, `human_checked`, `reviewer_notes`.

### Prompts
- `prompts/antigravity_master_prompt.txt`: 8-stage autonomous work-order.
- `prompts/README.md`: 18-prompt staged workflow sequence.

---

## 3. What Is Incomplete or Missing

| Item | Status | Notes |
|---|---|---|
| `beir` package | MISSING | Not installed; required for dataset loading |
| `sentence-transformers` | MISSING | Not installed; required for dense retrieval |
| `rank-bm25` | MISSING | Not installed; required for BM25 |
| `torch` | MISSING | Not installed; required by sentence-transformers |
| `data/hindi_queries.csv` | MISSING | Template only; translations not provided |
| `results/` directory | EMPTY | No experiments have been run |
| `src/` directory | EMPTY | No source modules beyond the script |
| Tests | MISSING | No test files exist anywhere |
| Visualizations | MISSING | No figures exist |
| Literature review PDF | MISSING | Referenced in master prompt but not in ZIP |
| Assignment/review PDFs | MISSING | Referenced in master prompt but not in ZIP |

---

## 4. Dependency Status

| Package | Required Version | Installed Version | Status |
|---|---|---|---|
| beir | >=2.0.0 | — | **MISSING** |
| sentence-transformers | >=3.0.0 | — | **MISSING** |
| rank-bm25 | >=0.2.2 | — | **MISSING** |
| pandas | >=2.0.0 | 3.0.1 | OK |
| numpy | >=1.24.0 | 2.4.3 | OK |
| scikit-learn | >=1.3.0 | 1.8.0 | OK |
| torch | >=2.1.0 | — | **MISSING** |
| PyYAML | >=6.0 | 6.0.3 | OK |

**Python version:** 3.14.2 (system Python, `C:\Python314\python.exe`)  
**Note:** Python 3.14 is very recent. `beir` and some deps may have compatibility issues — this requires testing.

---

## 5. Script Analysis

### `scripts/run_retrieval.py` — Strengths
- Modular functions: `tokenize()`, `recall_at_k()`, `reciprocal_rank_at_k()`, `load_hindi()`, `main()`
- Correct recall formula: `|relevant ∩ top_k| / |relevant|` (not just hit@k)
- MRR@10 computed as mean reciprocal rank across queries
- Skips queries with no relevant documents (returns `nan` for recall — correct)
- Failure case: queries where `reciprocal_rank_at_10 == 0`
- Hindi validation: checks required columns, ID alignment, duplicates, empty translations

### `scripts/run_retrieval.py` — Potential Issues to Verify
1. **BEIR API compatibility**: `beir>=2.0.0` API may differ from examples — needs testing
2. **Recall formula**: For single-relevant-doc queries, `|rel ∩ top_k| / |rel|` = 0 or 1 (binary). This is correct for SciFact where most queries have 1–2 relevant docs.
3. **Failure case definition**: `reciprocal_rank_at_10 == 0` catches all queries where no relevant doc is in top 10. VERIFIED correct.
4. **Hindi query coverage**: If hindi CSV has fewer IDs than English queries, only matching IDs are used. This asymmetry is handled correctly.
5. **Python 3.14 compatibility**: Very new — some packages may not have wheels yet.

---

## 6. Research Decisions Status

| Decision | Current Status | Evidence |
|---|---|---|
| Scope: SciFact cross-lingual retrieval | INFERRED | Proposed in research_decisions.md; instructor not yet confirmed |
| Three comparators (BM25, EN-dense, Multi-dense) | INFERRED | Listed in configs/experiment.yaml |
| Primary metric: Recall@5 | INFERRED | Listed in configs/experiment.yaml |
| Novelty claim | UNKNOWN | Literature search not yet done |
| Hindi translation quality | UNKNOWN | No translations exist yet |
| Environment compatibility | UNKNOWN | Dependencies not installed |

---

## 7. Generated Artifacts vs Source Files

| File | Type | Can be regenerated? |
|---|---|---|
| scripts/run_retrieval.py | Source | No (manually written) |
| configs/experiment.yaml | Source | No (protocol document) |
| data/hindi_queries_template.csv | Source | No (schema) |
| prompts/*.md, *.txt | Source | No (workflow design) |
| paper/paper_outline.md | Source | No (outline) |
| research_decisions.md | Source | No (decision log) |
| ai_assistance_log.md | Source | No (audit log) |
| baseline_validation.md | Source | No (validation log) |
| results/*.csv, *.json | Generated | Yes (run the script) |
| reports/* | Generated | Yes (this audit, future reports) |

---

## 8. Tasks Requiring External Data or Human Decisions

1. **Hindi translations**: Must be created by a human (or verified by a human if auto-generated). Cannot be automated without explicit authorization.
2. **Literature review PDFs**: Referenced in the master prompt but not in the ZIP. Cannot read them.
3. **Instructor approval**: `research_decisions.md` says "Proposed; instructor approval and source verification still needed."
4. **Bilingual review of Hindi translations**: Requires a human Hindi/English speaker.

---

## 9. Execution Plan

**Immediate next steps (autonomous):**
1. Install missing dependencies (`beir`, `sentence-transformers`, `rank-bm25`, `torch`)
2. Run smoke test (`--limit_queries 5 --languages en`)
3. If smoke test passes, run full English baseline
4. Create unit tests
5. Generate Hindi translations (draft, clearly labeled as machine-generated/unverified)
6. Create prompt inventory and execution log
7. Run full bilingual experiment after Hindi file is prepared
8. Generate visualizations from actual results
9. Draft paper from actual results

**Blockers:**
- Missing packages (will install)
- No Hindi translations (will generate draft, clearly labeled)
- Missing PDFs (will proceed without them)
