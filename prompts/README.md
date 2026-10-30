# Antigravity prompt sequence

Use these prompts one at a time. Do not ask Antigravity to generate a fake completed paper. At each stage, require it to stop and wait for real logs before advancing. The assignment expects 18 staged prompts, a validated baseline, real experiments, a 6–10 page evidence-grounded paper, a repository, an AI audit and a five-minute demonstration.

## Prompt 01 — Workspace and accountable mentor
You are my critical research mentor and pair programmer. My topic is “Evaluating Multilingual Reliability of Large Language Models in Scientific Literature Analysis.” Read `README.md`, `research_decisions.md`, and the two supplied PDFs if available. Summarize the assignment deliverables and the review's scope using citations to exact sections/pages. Mark claims VERIFIED, INFERRED, or UNKNOWN. Do not invent citations, data, executions, or results. Keep a portable decision log. Return only the current stage's output and ask me to approve before continuing.

## Prompt 02 — Evidence-based gap extraction
Analyze `multilingual_llm_review.pdf` critically. Extract methods, datasets, measured findings, author-reported limitations, and unresolved questions. Propose five testable gaps, each mapped to exact section/page/reference and labelled reported limitation vs your inference. Rank by significance, feasibility, and compute burden. Highlight any references or claims that must be checked against original publications. Do not claim novelty without a fresh search.

## Prompt 03 — Literature-to-experiment mapping
For the top three gaps, map original paper → method → dataset → official code/model → metric → limitation → minimum runnable baseline. Compare reproduction+extension, controlled comparison, and targeted modification. Recommend the smallest credible study for a student project with limited compute: SciFact cross-lingual evidence retrieval with BM25, English-only dense retrieval, and multilingual dense retrieval. Flag all assumptions and tell me what to verify manually.

## Prompt 04 — Novelty and feasibility gate
For the proposed study, create search strings for Google Scholar, ACL Anthology, Semantic Scholar, and arXiv around multilingual scientific retrieval, cross-lingual claim verification, SciFact, translated query evaluation, and multilingual dense retrieval. Do not invent search results. Give me a matrix for neighboring work, verified contribution, limitation, proposed difference, and evidence missing. Check dataset/model licenses and compute feasibility. End with GO / CONDITIONAL GO / NO-GO and a fallback.

## Prompt 05 — Research brief and questions
Prepare a one-page G1 brief. Proposed RQ1: How does retrieval effectiveness change between English scientific claims and Hindi-translated claims against the same English SciFact corpus? Proposed RQ2: Does a multilingual dense retriever reduce the Hindi–English retrieval gap relative to BM25 and an English-only dense retriever? Define variables, query/corpus protocol, primary metric Recall@5, secondary Recall@1/10 and MRR@10, controls, expected falsifying observations, limitations, and first executable milestone. Keep hypotheses as hypotheses, not findings.

## Prompt 06 — Dataset and baseline verification
Verify the official SciFact / BEIR source, license, structure, split, query IDs, qrels, corpus IDs, and relevance definitions from primary sources. Explain what SciFact can and cannot support. Compare BM25, `sentence-transformers/all-MiniLM-L6-v2`, and `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; verify their model cards and licenses. Explain leakage risks and why test qrels must not be used for tuning. Return a verification checklist, not assumed facts.

## Prompt 07 — Freeze the experiment protocol
Write a frozen protocol before seeing full results: same SciFact test queries and English corpus; English claims and ID-aligned Hindi translations; three retrievers; top-10 rankings; Recall@1/5/10 and MRR@10; seed 42; exact model IDs; corpus/query preprocessing; hardware/runtime logging; and failure-case inspection. Include Mermaid architecture, data flow, threat-to-validity table, translation provenance requirements, expected output schema, and change-control rules. Do not predict numeric results.

## Prompt 08 — Environment setup and smoke test
Inspect `requirements.txt` and `scripts/run_retrieval.py`. Give exact commands for Windows PowerShell and Linux, record Python/OS/CPU/GPU/RAM and package versions, install dependencies, and run `python scripts/run_retrieval.py --limit_queries 5 --languages en`. Do not claim compatibility or successful execution without my pasted logs. Stop after the smoke test and ask me for the actual console output.

## Prompt 09 — Implement one module at a time
Review the code module-by-module: dataset loader, ID alignment, BM25 ranking, dense embeddings, metric calculation, output serialization. Explain inputs/outputs and assumptions. Add unit tests for Recall@k and MRR@k, duplicate IDs, empty qrels, missing translations, and ranking ties. Make minimal changes only; give a test command for each change and wait for my actual output.

## Prompt 10 — Validate baseline against protocol
Compare the implementation and actual logs against the official dataset structure and protocol. Check data split, qrels relevance, ID alignment, tokenization, top-k ranking, embedding normalization, metric definitions, model identifiers, and deviations. Produce a report with VERIFIED / UNCERTAIN / NEEDS CORRECTION and exact evidence. Do not infer correctness merely because the script runs. No extension before this gate passes.

## Prompt 11 — Evidence-based debugging
When I paste a traceback, code, and output, identify confirmed facts separately from possible causes. Propose the smallest correction, explain it, add one regression test and one edge case, and say whether earlier runs must be repeated. Never invent a traceback or pretend you executed code. Update `ai_assistance_log.md` only with what actually occurred.

## Prompt 12 — Choose contribution and deeper analysis
After the baseline is validated, compare: (A) cross-lingual extension, (B) controlled comparison of three retrievers, (C) one justified modification. Recommend the controlled comparison plus failure analysis unless verified literature or resources justify otherwise. Define one deep analysis: Hindi-vs-English retrieval gap per method and manual categorization of top-10 failures using a documented rubric. Keep all original baselines intact.

## Prompt 13 — Evaluate actual outputs only
Use only actual result CSVs and logs. Validate query IDs, qrels, missing values, language coverage, and consistent method settings. Recompute Recall@1/5/10 and MRR@10 independently from saved rankings; export `retrieval_metrics.csv`, query-level outputs, and publication figures. If result files are absent, ask me to run the code. Do not create sample numbers or significance claims. Explain whether confidence intervals or paired tests are appropriate and their assumptions.

## Prompt 14 — Interpret results critically
Given my actual tables and failure cases, answer each RQ using direct observations, possible mechanisms, alternative explanations, and unsupported claims. Compare the English-to-Hindi gap per method, translation errors, domain/terminology effects, compute/runtime, and failures. State if results are inconclusive or negative. Do not say multilingual retrieval “solves hallucination”; retrieval metrics alone do not measure entailment, citation correctness, or end-to-end factuality. Suggest at most three high-value follow-ups.

## Prompt 15 — Draft evidence-grounded LaTeX paper
Use only verified sources, actual methods, saved settings, and genuine outputs. Draft a 6–10 page paper excluding references with Introduction, Related Work, Research Questions, Dataset, Methods, Experimental Setup, Results, Error Analysis, Threats to Validity, Conclusion, and Reproducibility. Write the abstract last. Mark missing facts [TO VERIFY]. Generate BibTeX only from checked metadata. Ensure every number matches CSVs and every figure can be regenerated.

## Prompt 16 — Hostile technical peer review
Review the draft as a skeptical reviewer. Audit novelty, claims, references, dataset suitability, translation confounds, fairness of baselines, metric definitions, test-set leakage, statistical claims, reproducibility, and limitations. Return major/minor issues with page/section and concrete fixes. Check every number against outputs and identify conclusions that exceed retrieval evidence. Do not praise fluency as scientific validity.

## Prompt 17 — Repository and reproduction documentation
Inspect actual repository files, commands, dependencies, licenses, data instructions, configuration, output CSVs, figures, and paper source. Write README reproduction steps and a clean repo tree. Mark every unexecuted command [TEST REQUIRED]. Do not commit raw data if prohibited, secrets, API keys, or fabricated outputs. Include environment capture (`pip freeze`), model IDs, translation provenance, limitations, and a second-student reproduction checklist.

## Prompt 18 — Human–AI provenance audit
Using the authentic prompt log, diffs, error messages, commands, and outputs I provide, create an AI-use report: task, prompt/tool, proposed change, human decision, verification, outcome, and evidence. Include at least three real examples only if I supply them; otherwise state the number available honestly. Reflect on what AI accelerated, what required human correction, what I learned, and remaining risks. Never invent interactions, commits, debugging stories, or results.
