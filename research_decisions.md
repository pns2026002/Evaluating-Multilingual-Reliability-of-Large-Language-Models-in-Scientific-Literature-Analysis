# Research Decisions Log

## Current status

- **VERIFIED from inspected repository and official BEIR source:** BEIR SciFact is an English-language scientific claim retrieval/fact-checking benchmark consisting of 5,183 scientific abstracts and 300 test queries (339 qrels judgments). Confirmed via automated check.
- **VERIFIED from runtime logs:** Retrieval pipeline runs cleanly on Windows 11 with Python 3.14.2, `beir 2.2.0`, `sentence-transformers 6.2.0`, `rank-bm25 0.2.2`, `torch 2.15.0+cpu`, and `transformers 5.0.0.dev0`.
- **VERIFIED from full 300-query bilingual experiment:** Script produced genuine `results/retrieval_metrics.csv`, `query_level_results.csv`, `failure_cases.csv`, and `run_metadata.json` across 1,800 query-level evaluations. Recomputation via independent validator matches saved results to < 1e-9 error. 37 unit tests in `tests/test_retrieval_utils.py` pass.
- **VERIFIED statistical findings:** Paired t-tests confirm statistically significant Hindi-English retrieval gaps across all methods ($p < 10^{-10}$): BM25 $\Delta_{\text{Recall@5}} = 0.6119 \pm 0.0541$, English Dense $\Delta_{\text{Recall@5}} = 0.7129 \pm 0.0507$, and Multilingual Dense $\Delta_{\text{Recall@5}} = 0.3542 \pm 0.0563$. Multilingual dense significantly outperforms English dense on Hindi queries ($+0.1508$, $t = 6.93, p < 10^{-6}$).
- **INFERRED:** A Hindi-query-to-English-corpus retrieval stress test measures cross-lingual retrieval under translated queries, not end-to-end multilingual literature analysis or naturally authored Hindi scientific information seeking.
- **UNKNOWN:** Whether the exact research question is novel. Conduct a fresh literature search before claiming novelty.
- **VERIFIED translation provenance:** All 300 test queries translated (89 via MyMemory API, 211 via local `Helsinki-NLP/opus-mt-en-hi`). All rows are explicitly flagged `human_checked=false`. Bilingual human review remains pending.

---

## Decision 1 — Narrow scope to cross-lingual evidence retrieval
- **Decision:** Use SciFact retrieval as the primary implementation milestone.
- **Reason:** Small, task-aligned scientific evidence corpus (5,183 documents); runnable on local CPU in minutes without paid APIs or GPU compute.
- **Review connection:** Motivates scientific reliability evaluation and cross-lingual retrieval/grounding measures.
- **Trade-off:** English-only corpus and translated Hindi queries limit external validity.
- **Status:** VERIFIED runnable, feasible, and completed.

---

## Decision 2 — Three retrieval comparators
- **Methods:**
  1. BM25 lexical retrieval (`rank-bm25` BM25Okapi, whitespace/punctuation tokenizer)
  2. English-only sentence embedding baseline (`sentence-transformers/all-MiniLM-L6-v2`)
  3. Multilingual sentence embedding model (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)
- **Reason:** Separates lexical matching, monolingual semantic retrieval, and cross-lingual semantic retrieval.
- **Status:** VERIFIED runnable and fully evaluated across 300 test claims.

---

## Decision 3 — Primary metrics and analysis
- **Primary:** Recall@5.
- **Secondary:** Recall@1, Recall@10, MRR@10.
- **Deep analysis:** Language gap by method ($\Delta = \text{Score}_{\text{English}} - \text{Score}_{\text{Hindi}}$), paired t-tests, plus failure-case inspection (queries with MRR@10 == 0).
- **Caution:** Retrieval metrics measure evidence location, not claim entailment, citation correctness, or end-to-end factual reliability.
- **Status:** FROZEN in `configs/experiment.yaml` and verified.

---

## Decision 4 — Hindi translation provenance and review policy
- **Decision:** Translate all 300 SciFact test queries using `MyMemoryTranslator` and local `Helsinki-NLP/opus-mt-en-hi` MarianMT model, preserving exact `query_id` alignment.
- **Provenance:** Every row in `data/hindi_queries.csv` records `query_id`, `english_text`, `hindi_text`, `translation_method`, `human_checked`, and `reviewer_notes`.
- **Policy:** Explicitly mark `human_checked=false`. Never present machine translations as human-verified or naturally authored Hindi.
- **Status:** COMPLETED (all 300 queries present and validated).

---

## Decision 5 — Corpus embedding disk caching
- **Decision:** Cache dense corpus embeddings to disk (`data/beir/corpus_emb_*.npy`).
- **Reason:** Encoding 5,183 abstracts takes ~2.5 minutes per model on CPU. Disk caching enables sub-second re-ranking runs and prevents duplicate compute.
- **Status:** IMPLEMENTED and VERIFIED in `scripts/run_retrieval.py`.

---

## Decision 6 — Empirical results and statistical significance
- **Decision:** Report exact empirical numbers and paired differences with 95% confidence intervals.
- **Verified Results (Test split, n=300 queries):**
  - English BM25: Recall@5 = 0.6969, MRR@10 = 0.5945
  - English Dense (`all-MiniLM-L6-v2`): Recall@5 = 0.7379, MRR@10 = 0.6047
  - English Multilingual Dense (`paraphrase-multilingual-MiniLM-L12-v2`): Recall@5 = 0.5300, MRR@10 = 0.4550
  - Hindi BM25: Recall@5 = 0.0850, MRR@10 = 0.0744
  - Hindi Dense (`all-MiniLM-L6-v2`): Recall@5 = 0.0250, MRR@10 = 0.0206
  - Hindi Multilingual Dense (`paraphrase-multilingual-MiniLM-L12-v2`): Recall@5 = 0.1758, MRR@10 = 0.1333
- **Hindi–English Gap $\Delta$:**
  - BM25: $\Delta_{\text{Recall@5}} = +0.6119 \pm 0.0541$ ($t=22.18, p<10^{-10}$)
  - English Dense: $\Delta_{\text{Recall@5}} = +0.7129 \pm 0.0507$ ($t=27.55, p<10^{-10}$)
  - Multilingual Dense: $\Delta_{\text{Recall@5}} = +0.3542 \pm 0.0563$ ($t=12.33, p<10^{-10}$)
- **Status:** COMPLETED and VERIFIED.

---

## Decision 7 — Qualitative error modes
- **Decision:** Categorize failure cases (RR@10 == 0) into 5 distinct error modes:
  1. Lexical mismatch across scripts (Devanagari vs Latin characters in BM25)
  2. Terminology mismatch in scientific domains (e.g. "inductive" translated as mathematical/philosophical "आगमनात्मक")
  3. Machine translation syntactic/semantic artifacts (e.g. "compromises" translated as "समझौता करती है")
  4. Cross-lingual dense space misalignment for specialized biomedical entities
  5. Capacity trade-off / "curse of multilinguality" (multilingual model scores lower than English model on English queries: 0.530 vs 0.738)
- **Status:** COMPLETED and documented in research paper and reports.

---

## Completed Actions
1. Audited repository tree and dependencies (`reports/repository_audit.md`).
2. Cataloged prompt inventory (`reports/prompt_inventory.md`).
3. Installed missing packages: `beir`, `sentence-transformers`, `rank-bm25`, `torch`, `requests`, `deep-translator`, `transformers`, `sentencepiece`.
4. Created 37 unit tests covering `recall_at_k`, `reciprocal_rank_at_k`, `tokenize`, `load_hindi`, and aggregation (`tests/test_retrieval_utils.py`). All passed.
5. Executed 5-query English smoke test (`results/retrieval_metrics.csv`).
6. Built metric validator (`scripts/validate_metrics.py`) and verified 100% agreement between query-level results and aggregate metrics.
7. Generated all 300 Hindi translations with transparent provenance (`data/hindi_queries.csv`).
8. Implemented corpus embedding disk caching in `scripts/run_retrieval.py`.
9. Executed full bilingual experiment on all 300 test queries across 3 methods (1,800 query runs).
10. Validated all metrics independently (`results/retrieval_metrics_recomputed.csv`).
11. Created 4 publication-ready figures (`reports/figures/fig1_metric_comparison.png`, `fig2_hindi_english_gap.png`, `fig3_recall5_distributions.png`, `fig4_failure_rates.png`).
12. Conducted statistical significance testing and qualitative error mode analysis.
13. Recorded frozen environment in `results/pip_freeze.txt`.
14. Finalized research paper draft (`paper/draft_paper.md`) and LaTeX scaffold (`paper/main.tex`).
