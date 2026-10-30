# Implementation Paper Outline (do not invent results)

Working title: Cross-Lingual Scientific Evidence Retrieval: Measuring the Hindi–English Retrieval Gap on SciFact

1. Abstract — write last, from actual results only.
2. Introduction — motivate multilingual scientific access; distinguish multilingual capability from scientific reliability.
3. Related Work — verify original sources from the prior review; include close cross-lingual retrieval and scientific claim verification work.
4. Research Questions — RQ1: How does retrieval effectiveness change between English claims and Hindi-translated claims against an English scientific corpus? RQ2: Does the multilingual dense retriever reduce the cross-lingual retrieval gap relative to BM25 and an English-only dense retriever?
5. Dataset and Protocol — SciFact version/split, query translations and review, corpus language, qrels, models, settings, environment.
6. Methods — BM25, English dense encoder, multilingual dense encoder; explain ranking and metrics.
7. Results — insert actual `retrieval_metrics.csv` values and uncertainty analysis if performed. Never use placeholders as if they were findings.
8. Error Analysis — manually inspect top-10 failures and categorize translation/terminology/lexical/semantic mismatch only with a documented coding protocol.
9. Threats to Validity — translated queries, language pair, domain coverage, corpus language, metrics, model choice, limited sample.
10. Conclusion — answer RQs proportionally to measured evidence.
11. Reproducibility — repo commit, commands, package versions, hardware, model IDs, data license and translation provenance.
