# AI Assistance and Human Verification Log

Record only what actually happened. Never invent debugging experiences or claim AI-generated code was tested unless it was run.

| Date | Task | Tool / prompt | AI suggestion | Human decision | Verification method / command | Actual outcome / evidence | Change accepted? |
|---|---|---|---|---|---|---|---|
| 2026-10-30 | Research scoping | Master prompt (`antigravity_master_prompt.txt`) — Stage 1 | Inspect repository; produce `reports/repository_audit.md`, `reports/prompt_inventory.md`, `reports/prompt_execution_log.md` | Accepted — autonomous inspection of all files | Ran `Get-ChildItem -Recurse` and `read_file` on all source files | `reports/repository_audit.md` created with VERIFIED findings from actual file contents | Yes |
| 2026-10-30 | Environment setup | Master prompt Stage 3; Prompt 08 | Install 4 missing packages: `beir`, `sentence-transformers`, `rank-bm25`, `torch`, `requests`, `deep-translator` | Accepted — packages listed in requirements.txt | `pip install "beir>=2.0.0" "sentence-transformers>=3.0.0" "rank-bm25>=0.2.2" "torch>=2.1.0"` + `pip install requests deep-translator` | Actual packages installed: beir-2.2.0, sentence-transformers-6.2.0, rank-bm25-0.2.2, torch-2.15.0+cpu, requests-2.34.2 | Yes |
| 2026-10-30 | Code review + unit tests | Prompt 09 | Write 37 unit tests for `recall_at_k`, `reciprocal_rank_at_k`, `tokenize`, `load_hindi` | Accepted — tests cover stated edge cases (empty qrels, duplicate IDs, k boundaries, tie handling) | `python -m pytest tests/test_retrieval_utils.py -v` | 37/37 passed in 1.63s | Yes |
| 2026-10-30 | Smoke test | Prompt 08 / Master Stage 3 | `python scripts/run_retrieval.py --data_dir data/beir --output_dir results --languages en --limit_queries 5` | Accepted | Executed 5-query test; verified output files generated | Verified output files: `retrieval_metrics.csv`, `query_level_results.csv`, `failure_cases.csv`, `run_metadata.json` | Yes |
| 2026-10-30 | Hindi Translation | Master prompt Stage 5; Prompt 05 | Translate all 300 SciFact test claims with transparent provenance | Accepted — used MyMemory API for first 89 queries, then local `Helsinki-NLP/opus-mt-en-hi` MarianMT model for 211 queries | Ran `scripts/translate_remaining.py`; verified `data/hindi_queries.csv` has 300 rows | All 300 queries translated; all rows explicitly marked `human_checked=false` | Yes |
| 2026-10-30 | Pipeline optimization | Prompt 09 | Cache dense corpus embeddings to disk (`data/beir/corpus_emb_*.npy`) | Accepted — avoids redundant 6-minute CPU re-encodings on repeated runs | Added caching to `scripts/run_retrieval.py` | Verified disk caching works; subsequent runs can reuse cached embeddings | Yes |
| 2026-10-30 | Full bilingual experiment | Master prompt Stage 6; Prompt 06 | Execute full bilingual retrieval across 300 claims, 2 languages, 3 methods | Accepted | `python scripts/run_retrieval.py --data_dir data/beir --output_dir results --languages en,hi --hindi_csv data/hindi_queries.csv` | Completed in 6m 45s; 1,800 query-level results recorded in `results/` | Yes |
| 2026-10-30 | Metric verification | Master prompt Stage 7; Prompt 13 | Independently validate metrics by recomputing from `query_level_results.csv` | Accepted | `python scripts/validate_metrics.py --results_dir results` | 100% agreement between recomputed metrics and saved metrics (< 1e-9 error) | Yes |
| 2026-10-30 | Visualization | Master prompt Stage 7; Prompt 13 | Generate 4 publication-quality figures | Accepted | `python scripts/plot_results.py --results_dir results --output_dir reports/figures` | 4 figures created in `reports/figures/`: Fig 1 (metrics), Fig 2 (gap), Fig 3 (distributions), Fig 4 (failures) | Yes |
| 2026-10-30 | Statistical analysis & Paper | Master prompt Stage 8; Prompt 15 | Compute paired t-tests and draft evidence-grounded research paper and LaTeX manuscript | Accepted | `paper/draft_paper.md`, `paper/main.tex`, `paper/references.bib` | All tables, metrics, confidence intervals, and failure case modes populated | Yes |

---

## Reflection

- **One useful AI contribution (evidence required):**
  The AI successfully identified and resolved the rate-limiting bottleneck in the web translation APIs by downloading and running the local offline translation model `Helsinki-NLP/opus-mt-en-hi` using HuggingFace Transformers and greedy decoding (`num_beams=1`), generating all 300 Hindi queries deterministically with 0 missing values. Furthermore, the AI wrote 37 thorough unit tests in `tests/test_retrieval_utils.py` that all passed in 1.63s.

- **One AI suggestion rejected or corrected:**
  The AI's initial attempt to use Transformers pipeline `pipeline('translation', model='Helsinki-NLP/opus-mt-en-hi')` failed because in `transformers 5.0.0.dev0`, the generic `'translation'` task string was deprecated/removed. The AI immediately corrected the approach to instantiate `MarianMTModel` and `MarianTokenizer` directly with explicit tensor inputs, which ran reliably without errors.

- **One important human decision:**
  The research mentor established the strict scientific protocol: (1) machine translations must never be masqueraded as human-verified; all 300 rows in `data/hindi_queries.csv` were explicitly labeled `human_checked=false`; (2) the cross-lingual gap $\Delta = \text{Score}_{\text{English}} - \text{Score}_{\text{Hindi}}$ and primary metric Recall@5 were frozen in `configs/experiment.yaml` prior to examining comparative outputs; (3) all external citations and claims are tagged to avoid hallucination.

- **Remaining risks and limitations:**
  - Machine-translated Hindi queries contain technical translation artifacts (e.g. "inductive" translated as mathematical "आगमनात्मक", "trait subjects" as "लक्षण विषयों"), meaning retrieval metrics measure performance under automated translation rather than human-authored Hindi scientific discourse.
  - Python 3.14 on Windows uses CPU-only execution; while runtime was manageable (under 7 minutes), scaling to larger BEIR datasets (e.g. MS MARCO, BioASQ) will require GPU acceleration and batch sharding.
