#!/usr/bin/env python3
"""Independently recompute and validate retrieval metrics from saved rankings.

This script re-reads query_level_results.csv and recomputes aggregate metrics
from scratch to verify correctness of the main pipeline output.
Also produces a failure case analysis report.

Usage:
    python scripts/validate_metrics.py --results_dir results
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def recall_at_k(ranked_ids_str: str, relevant_ids: set, k: int) -> float:
    """Recompute recall@k from space-separated doc_id string."""
    if not relevant_ids:
        return np.nan
    ranked = ranked_ids_str.split()[:k]
    return len(set(ranked) & relevant_ids) / len(relevant_ids)


def reciprocal_rank_at_k(ranked_ids_str: str, relevant_ids: set, k: int) -> float:
    ranked = ranked_ids_str.split()[:k]
    for i, doc_id in enumerate(ranked, 1):
        if doc_id in relevant_ids:
            return 1.0 / i
    return 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    query_path = results_dir / "query_level_results.csv"
    metrics_path = results_dir / "retrieval_metrics.csv"
    metadata_path = results_dir / "run_metadata.json"

    if not query_path.exists():
        print(f"ERROR: {query_path} not found. Run the experiment first.", file=sys.stderr)
        sys.exit(1)

    qdf = pd.read_csv(query_path)
    print(f"Loaded {len(qdf)} query-level rows from {query_path}")
    print(f"Columns: {list(qdf.columns)}")
    print(f"Languages: {sorted(qdf['language'].unique())}")
    print(f"Methods: {sorted(qdf['method'].unique())}")
    print()

    # -----------------------------------------------------------------------
    # Validation 1: Recompute aggregate metrics from saved query-level rows
    # -----------------------------------------------------------------------
    print("=== VALIDATION: Recomputed aggregate metrics ===")
    recomputed_rows = []
    for (lang, method), grp in qdf.groupby(["language", "method"]):
        n = len(grp)
        mrr = grp["reciprocal_rank_at_10"].mean()
        r1 = grp["recall_at_1"].mean()
        r5 = grp["recall_at_5"].mean()
        r10 = grp["recall_at_10"].mean()
        recomputed_rows.append({
            "language": lang, "method": method, "n_queries": n,
            "MRR@10_recomputed": mrr,
            "Recall@1_recomputed": r1,
            "Recall@5_recomputed": r5,
            "Recall@10_recomputed": r10,
        })

    rdf = pd.DataFrame(recomputed_rows).sort_values(["language", "method"])
    print(rdf.to_string(index=False))
    print()

    # Compare against saved metrics.csv
    if metrics_path.exists():
        saved = pd.read_csv(metrics_path).sort_values(["language", "method"]).reset_index(drop=True)
        rdf_sorted = rdf.sort_values(["language", "method"]).reset_index(drop=True)
        print("=== COMPARISON: Saved vs Recomputed ===")
        all_match = True
        for _, row in rdf_sorted.iterrows():
            lang, method = row["language"], row["method"]
            saved_row = saved[(saved["language"] == lang) & (saved["method"] == method)]
            if saved_row.empty:
                print(f"  MISSING in saved metrics: {lang}/{method}")
                continue
            for metric, col in [("MRR@10", "MRR@10_recomputed"),
                                 ("Recall@1", "Recall@1_recomputed"),
                                 ("Recall@5", "Recall@5_recomputed"),
                                 ("Recall@10", "Recall@10_recomputed")]:
                saved_val = float(saved_row[metric].values[0])
                recomputed_val = float(row[col])
                match = abs(saved_val - recomputed_val) < 1e-9
                status = "OK" if match else "MISMATCH"
                if not match:
                    all_match = False
                    print(f"  {status}: {lang}/{method}/{metric}: saved={saved_val:.6f}, recomputed={recomputed_val:.6f}")
        if all_match:
            print("  All metrics match between saved CSV and recomputed values. VERIFIED.")
    else:
        print(f"  {metrics_path} not found; skipping comparison.")
    print()

    # -----------------------------------------------------------------------
    # Validation 2: Check for missing relevant-document mappings
    # -----------------------------------------------------------------------
    print("=== Validation: Query-level sanity checks ===")
    print(f"  Total query-level rows: {len(qdf)}")
    print(f"  NaN recall_at_5 rows: {qdf['recall_at_5'].isna().sum()} (queries with 0 relevant docs — should be 0)")
    print(f"  NaN recall_at_1 rows: {qdf['recall_at_1'].isna().sum()}")
    print(f"  NaN reciprocal_rank_at_10 rows: {qdf['reciprocal_rank_at_10'].isna().sum()}")
    total_failures = (qdf["reciprocal_rank_at_10"] == 0).sum()
    print(f"  Queries with RR@10=0 (failure cases): {total_failures} / {len(qdf)} ({100*total_failures/len(qdf):.1f}%)")
    print()

    # -----------------------------------------------------------------------
    # Validation 3: Failure case analysis
    # -----------------------------------------------------------------------
    print("=== Failure Case Analysis (RR@10 == 0) ===")
    failures = qdf[qdf["reciprocal_rank_at_10"] == 0].copy()
    if failures.empty:
        print("  No failure cases (all queries had at least one relevant doc in top 10).")
    else:
        for (lang, method), grp in failures.groupby(["language", "method"]):
            pct = 100 * len(grp) / len(qdf[(qdf["language"] == lang) & (qdf["method"] == method)])
            print(f"  {lang}/{method}: {len(grp)} failures ({pct:.1f}%)")

    # Print sample failure cases
    if not failures.empty and "top10_doc_ids" in failures.columns:
        print("\n  Sample failure cases (first 5 failures for bm25/en):")
        sample = failures[(failures["language"] == "en") & (failures["method"] == "bm25")]
        for _, row in sample.head(5).iterrows():
            print(f"    query_id={row['query_id']} | num_relevant={row.get('num_relevant_docs', '?')}")

    print()

    # -----------------------------------------------------------------------
    # Metadata check
    # -----------------------------------------------------------------------
    if metadata_path.exists():
        meta = json.loads(metadata_path.read_text(encoding="utf-8"))
        print("=== Run Metadata ===")
        for k, v in meta.items():
            print(f"  {k}: {v}")
    else:
        print(f"  run_metadata.json not found.")

    # Save recomputed metrics
    out_path = results_dir / "retrieval_metrics_recomputed.csv"
    rdf_out = rdf.rename(columns={
        "MRR@10_recomputed": "MRR@10",
        "Recall@1_recomputed": "Recall@1",
        "Recall@5_recomputed": "Recall@5",
        "Recall@10_recomputed": "Recall@10",
    })[["language", "method", "n_queries", "MRR@10", "Recall@1", "Recall@5", "Recall@10"]]
    rdf_out.to_csv(out_path, index=False)
    print(f"\nSaved recomputed metrics: {out_path}")


if __name__ == "__main__":
    main()
