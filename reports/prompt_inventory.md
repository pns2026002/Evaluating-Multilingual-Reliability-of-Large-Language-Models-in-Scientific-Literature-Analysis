# Prompt Inventory

**Created:** 2026-10-30  
**Source:** Direct inspection of `prompts/` directory and all prompt files in the repository.

---

## Discovered Prompt Files

| # | File | Size | Description |
|---|---|---|---|
| 1 | `prompts/antigravity_master_prompt.txt` | 29 lines | 8-stage autonomous work-order for the AI assistant |
| 2 | `prompts/README.md` | 57 lines | 18-prompt staged workflow sequence for human-AI pair programming |

---

## Prompt 1: `prompts/antigravity_master_prompt.txt`

**Intended purpose:** Configure the AI assistant as a "critical scientific mentor and pair programmer" with non-negotiable rules: no fabrication, staged work, protocol freeze, evidence-only paper writing.

**Required inputs:** Access to README.md, research_decisions.md, baseline_validation.md, ai_assistance_log.md, configs/experiment.yaml, scripts/, prompts/README.md, and assignment/review PDFs (if available).

**Expected outputs:** Critical gap-to-experiment map (Stage 1), GO/NO-GO checklist (Stage 2), smoke test logs (Stage 3), baseline audit (Stage 4), Hindi translations (Stage 5), full experiment outputs (Stage 6), metrics/plots/failure cases (Stage 7), paper/README/validation/AI provenance report (Stage 8).

**Dependencies:** All repository files; Python environment; BEIR/SciFact access; sentence-transformers.

**Execution order:** Stages 1–8 in sequence. Stop-for-logs after each stage.

**Non-negotiable rules (from the prompt):**
1. No fabrication of papers, URLs, citations, metrics, figures, code execution, or AI experiences.
2. Mark claims VERIFIED / INFERRED / UNKNOWN.
3. Do not write results until real output files exist and have been checked.
4. Use staged work; stop for logs before advancing.
5. Do not replace files or refactor without explanation.
6. Preserve a simple reproducible experiment: BEIR SciFact, English corpus, English + Hindi translated queries, BM25 + EN dense + multilingual dense, Recall@1/5/10 + MRR@10.
7. Treat Hindi data as translated-query stress test, not naturally authored Hindi science.
8. Keep retrieval claims narrow (not factual entailment or citation correctness).
9. Freeze protocol before inspecting full comparative results.
10. Create paper text only from verified literature and actual outputs; mark gaps [TO VERIFY].

**Project stage:** Governs all stages (meta-prompt / system configuration).

---

## Prompt 2: `prompts/README.md` — 18-Prompt Staged Sequence

Each sub-prompt below maps to one workflow stage.

| Prompt | ID | Title | Stage | Required inputs | Expected outputs |
|---|---|---|---|---|---|
| 01 | Workspace and accountable mentor | Repository initialization | README.md, research_decisions.md, review PDFs | Summary of deliverables; VERIFIED/INFERRED/UNKNOWN claims; portable decision log |
| 02 | Evidence-based gap extraction | Literature analysis | multilingual_llm_review.pdf | 5 testable gaps with section/page citations; novelty and feasibility ranking |
| 03 | Literature-to-experiment mapping | Study design | Top 3 gaps from Prompt 02 | Reproduction+extension vs controlled comparison analysis; minimum runnable baseline |
| 04 | Novelty and feasibility gate | GO/NO-GO decision | Search strings for multiple databases | Neighboring work matrix; license/compute feasibility; GO / CONDITIONAL GO / NO-GO |
| 05 | Research brief and questions | Protocol definition | RQ1/RQ2 draft | One-page G1 brief; variable definitions; expected falsifying observations; first milestone |
| 06 | Dataset and baseline verification | Source verification | SciFact/BEIR docs; model cards | Verification checklist for dataset, models, licenses, leakage risks |
| 07 | Freeze the experiment protocol | Protocol freeze | Verified dataset/model info | Frozen protocol document; Mermaid architecture; data flow; threat-to-validity table |
| 08 | Environment setup and smoke test | Environment verification | requirements.txt, run_retrieval.py | Exact setup commands; version log; 5-query smoke test output |
| 09 | Implement one module at a time | Code review and testing | run_retrieval.py | Unit tests for Recall@k, MRR@k, edge cases; minimal code changes |
| 10 | Validate baseline against protocol | Baseline gate | Actual logs from Prompt 08 | VERIFIED/UNCERTAIN/NEEDS CORRECTION checklist; deviation report |
| 11 | Evidence-based debugging | Debugging | Actual traceback + code + output | Smallest confirmed correction; one regression test; one edge-case test |
| 12 | Choose contribution and deeper analysis | Analysis design | Validated baseline | Comparison of contribution options; failure analysis rubric |
| 13 | Evaluate actual outputs only | Metric computation | Actual result CSVs and logs | Independent metric recomputation; retrieval_metrics.csv; query-level outputs; figures |
| 14 | Interpret results critically | Results interpretation | Actual tables and failure cases | RQ answers with mechanisms, alternatives, unsupported claims identified |
| 15 | Draft evidence-grounded LaTeX paper | Paper writing | Verified sources + actual outputs | Full paper draft; BibTeX from checked metadata |
| 16 | Hostile technical peer review | Paper review | Paper draft | Major/minor issues with page/section references; numbers checked against outputs |
| 17 | Repository and reproduction documentation | Repository cleanup | Actual repo files and commands | README reproduction steps; clean repo tree; reproduction checklist |
| 18 | Human–AI provenance audit | AI audit | Authentic prompt log, diffs, errors | AI-use report: task, prompt, change, decision, verification, outcome |

---

## Missing Prompt Categories

The following workflow stages **do not have dedicated prompt files** in the repository, but are covered by the 18-prompt sequence in `prompts/README.md`:

| Missing category | Covered by |
|---|---|
| Visualization/plotting | Prompt 13 (outputs), Prompt 15 (paper figures) |
| Failure analysis | Prompt 12 and 14 |
| Citation verification | Prompt 15 and 16 |
| Statistical analysis | Prompt 13 and 14 |

---

## Prompt-to-Stage Mapping (Execution Order)

```
Stage A (Environment):   Prompt 08 → verify environment → install deps → smoke test
Stage B (Protocol):      Prompts 01–07 → already done as repository scaffold
Stage C (Implementation):Prompt 09 → code review + unit tests
Stage D (Validation):    Prompt 10 → baseline validation gate
Stage E (Hindi):         Prompt 05, 06 → Hindi translation workflow
Stage F (Full Exp):      Prompt 13 → run full experiment; evaluate outputs
Stage G (Analysis):      Prompts 12, 14 → failure analysis; results interpretation
Stage H (Paper):         Prompts 15, 16 → draft paper; peer review
Stage I (Docs):          Prompts 17, 18 → repo docs; AI provenance audit
```

---

## Notes

- `multilingual_llm_review.pdf` referenced by Prompt 02 is **NOT in the repository**. Prompts 02–04 cannot be fully executed without it.
- Prompt 18 requires authentic prompt log, diffs, and error outputs — these will be collected during execution.
- Prompts 01–07 correspond to planning stages that are already partially materialized in the repository scaffolding (research_decisions.md, configs/experiment.yaml, paper/paper_outline.md).
