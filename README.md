# Multilingual Reliability of LLMs in Scientific Literature Analysis — Starter Repository

This is a **research starter kit**, not a completed experimental paper. It contains an executable retrieval baseline and research workflow scaffolds. No results are prefilled. Run the experiment and report only outputs generated on your machine.

## Proposed minimum viable study

**Working title:** Cross-Lingual Scientific Evidence Retrieval: Measuring the Hindi–English Retrieval Gap on SciFact

**Research question:** When scientific claims are submitted in English versus Hindi, how do lexical retrieval and English-only versus multilingual dense retrieval differ in retrieving the evidence abstracts associated with those claims from an English scientific corpus?

**Why this is a tractable first study:** Your review identifies English-centric literature-analysis evaluation, weak non-English scientific coverage, language/domain confounding, and the need to report retrieval recall and evidence alignment (review §§6–7). SciFact provides scientific claims and evidence-bearing abstracts, but its source dataset is English-only. Therefore, Hindi queries must be treated as a *translated-query stress test*, not as naturally authored Hindi science. Translation quality is a threat to validity and must be documented.

**Comparators:** (1) BM25 lexical retrieval, (2) English-only sentence embeddings (`sentence-transformers/all-MiniLM-L6-v2`), and (3) multilingual sentence embeddings (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`). Compare English queries and independently reviewed Hindi translations against the same English corpus.

**Primary metrics:** Recall@1, Recall@5, Recall@10, MRR@10. The script also records query count and missing-query counts. Treat these as retrieval metrics, not as complete scientific factuality or citation reliability.

**Deep analysis:** Compare the Hindi-vs-English performance gap by retrieval method and inspect failure cases. Optionally stratify by claim length or evidence count after the basic pipeline is validated.

## Status labels

- **VERIFIED:** directly supported by a cited source or genuine execution output.
- **INFERRED:** a plausible research interpretation that still needs testing.
- **UNKNOWN:** not checked yet.

## Setup (Python 3.10 or 3.11 recommended)

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Dataset

The code downloads the BEIR SciFact corpus, queries, and test qrels through the BEIR loader. The dataset is English-only and includes roughly 5k scientific abstracts and 300 test queries in the standard BEIR version. Check the dataset card and terms before reuse:
- https://huggingface.co/datasets/BeIR/scifact
- https://github.com/allenai/scifact
- BEIR project: https://github.com/beir-cellar/beir

First run:

```bash
python scripts/run_retrieval.py --data_dir data/beir --output_dir results --languages en
```

For Hindi stress testing, create `data/hindi_queries.csv` using `data/hindi_queries_template.csv` as a schema. Each row must contain `query_id`, `english_text`, `hindi_text`, `translation_method`, and `human_checked` (true/false). Preserve the original query ID. Translate only the query text; do not translate the corpus for this experiment. Ideally, have a bilingual reviewer check the Hindi text and record edits. Never represent machine translations as naturally authored Hindi.

Then run:

```bash
python scripts/run_retrieval.py --data_dir data/beir --output_dir results --languages en,hi --hindi_csv data/hindi_queries.csv
```

**Important:** The Hindi run will stop with a helpful message if the Hindi CSV is missing. It does not fabricate translations.

## Outputs

- `results/retrieval_metrics.csv`: actual metric values by language and retrieval method.
- `results/query_level_results.csv`: query-level reciprocal rank and hit/recall information.
- `results/run_metadata.json`: configuration, model names, seed, data split, and timestamp.
- `results/failure_cases.csv`: queries for which a method fails to retrieve a relevant abstract in top 10.
- `results/pip_freeze.txt`: exact installed environment freeze.
- `reports/figures/`: publication-ready figures (metric comparisons, Hindi-English gap, recall distributions, failure rates).

## Reproduction Commands

```bash
# 1. Run full bilingual experiment across English and Hindi claims
python scripts/run_retrieval.py --data_dir data/beir --output_dir results --languages en,hi --hindi_csv data/hindi_queries.csv

# 2. Independently validate and recompute metrics from query-level output
python scripts/validate_metrics.py --results_dir results

# 3. Generate publication-ready figures
python scripts/plot_results.py --results_dir results --output_dir reports/figures

# 4. Run unit test suite
python -m pytest tests/test_retrieval_utils.py -v
```

## Limitations to state

1. SciFact is English-only; Hindi queries are translated stress tests rather than naturally authored Hindi scientific claims.
2. Translation can change terminology, negation, numbers, or claim meaning.
3. Retrieval recall does not establish that a retrieved abstract entails the claim or that the final answer is factually correct.
4. The English-only dense encoder is a useful control but not necessarily a strong baseline for cross-lingual retrieval.
5. One language pair and one biomedical/scientific dataset do not support claims about all languages or all scientific domains.
6. Model versions, package versions, hardware and runtime should be recorded.

## Project structure

- `scripts/run_retrieval.py` — retrieval baselines and evaluation
- `data/hindi_queries_template.csv` — translation annotation schema, not data
- `configs/experiment.yaml` — frozen planned settings
- `research_decisions.md` — decision record
- `prompts/` — customized AI prompts aligned to the course's 18-prompt sequence
- `ai_assistance_log.md` — record real prompts, decisions, checks and outputs
- `baseline_validation.md` — record actual validation evidence
- `paper/` — manuscript scaffold; do not fill Results until real runs exist

## Reproducibility

Freeze the dataset split, model identifiers, top-k values and primary metric before examining comparative results. Save the full console output and environment (`pip freeze > results/pip_freeze.txt`). Do not tune on the test set. If you change the protocol after seeing results, log the change and explain why.
