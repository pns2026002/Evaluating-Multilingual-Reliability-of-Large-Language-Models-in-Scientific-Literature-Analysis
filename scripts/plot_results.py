#!/usr/bin/env python3
"""Generate all research visualizations from actual experiment outputs.

Reads results/retrieval_metrics.csv and results/query_level_results.csv.
Saves figures to reports/figures/.

Usage:
    python scripts/plot_results.py --results_dir results --output_dir reports/figures

All figures are generated from actual experiment output only.
Do not modify this script to use hardcoded or example data.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker


METHODS_ORDER = ["bm25", "english_dense", "multilingual_dense"]
METHOD_LABELS = {
    "bm25": "BM25",
    "english_dense": "EN-Dense\n(MiniLM-L6)",
    "multilingual_dense": "Multi-Dense\n(mMiniLM-L12)",
}
LANG_COLORS = {"en": "#1f77b4", "hi": "#ff7f0e"}
LANG_LABELS = {"en": "English", "hi": "Hindi"}
METRIC_COLS = ["Recall@1", "Recall@5", "Recall@10", "MRR@10"]


def load_data(results_dir: Path):
    metrics_path = results_dir / "retrieval_metrics.csv"
    query_path = results_dir / "query_level_results.csv"
    failures_path = results_dir / "failure_cases.csv"

    if not metrics_path.exists():
        print(f"ERROR: {metrics_path} not found. Run the experiment first.", file=sys.stderr)
        sys.exit(1)

    metrics = pd.read_csv(metrics_path)
    query_df = pd.read_csv(query_path) if query_path.exists() else None
    failures = pd.read_csv(failures_path) if failures_path.exists() else None
    return metrics, query_df, failures


def fig1_metric_comparison_bar(metrics: pd.DataFrame, out_dir: Path):
    """Figure 1: Grouped bar chart — all metrics by method and language."""
    languages = sorted(metrics["language"].unique())
    methods = [m for m in METHODS_ORDER if m in metrics["method"].unique()]
    n_metrics = len(METRIC_COLS)
    n_methods = len(methods)

    fig, axes = plt.subplots(1, n_metrics, figsize=(14, 5), sharey=False)
    if n_metrics == 1:
        axes = [axes]

    x = np.arange(n_methods)
    width = 0.35

    for ax_idx, metric in enumerate(METRIC_COLS):
        ax = axes[ax_idx]
        for lang_idx, lang in enumerate(languages):
            lang_data = metrics[metrics["language"] == lang]
            vals = []
            for m in methods:
                row = lang_data[lang_data["method"] == m]
                vals.append(float(row[metric].values[0]) if not row.empty else np.nan)
            offset = (lang_idx - 0.5) * width
            bars = ax.bar(x + offset, vals, width,
                          label=LANG_LABELS.get(lang, lang),
                          color=LANG_COLORS.get(lang, f"C{lang_idx}"),
                          alpha=0.85, edgecolor="white")
            for bar, val in zip(bars, vals):
                if not np.isnan(val):
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                            f"{val:.3f}", ha="center", va="bottom", fontsize=7)

        ax.set_title(metric, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([METHOD_LABELS.get(m, m) for m in methods], fontsize=8)
        ax.set_ylim(0, 1.0)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.2f"))
        ax.grid(axis="y", alpha=0.3)
        if ax_idx == 0:
            ax.set_ylabel("Score")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", fontsize=9)
    fig.suptitle("Retrieval Metrics by Method and Query Language\n(SciFact test set, English corpus)",
                 fontsize=11, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 0.88, 0.95])
    path = out_dir / "fig1_metric_comparison.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def fig2_hindi_english_gap(metrics: pd.DataFrame, out_dir: Path):
    """Figure 2: Hindi–English performance gap (Delta = EN - HI) for each metric and method."""
    if "hi" not in metrics["language"].unique():
        print("Skipping Fig2: no Hindi results.")
        return
    methods = [m for m in METHODS_ORDER if m in metrics["method"].unique()]
    gaps = {metric: [] for metric in METRIC_COLS}
    for m in methods:
        en_row = metrics[(metrics["language"] == "en") & (metrics["method"] == m)]
        hi_row = metrics[(metrics["language"] == "hi") & (metrics["method"] == m)]
        for metric in METRIC_COLS:
            en_val = float(en_row[metric].values[0]) if not en_row.empty else np.nan
            hi_val = float(hi_row[metric].values[0]) if not hi_row.empty else np.nan
            gaps[metric].append(en_val - hi_val)

    x = np.arange(len(methods))
    fig, ax = plt.subplots(figsize=(10, 5))
    width = 0.18
    colors = plt.cm.Set2.colors  # type: ignore[attr-defined]
    for i, metric in enumerate(METRIC_COLS):
        offset = (i - 1.5) * width
        bars = ax.bar(x + offset, gaps[metric], width,
                      label=metric, color=colors[i], alpha=0.85, edgecolor="white")
        for bar, val in zip(bars, gaps[metric]):
            if not np.isnan(val):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + (0.002 if val >= 0 else -0.012),
                        f"{val:+.3f}", ha="center", va="bottom", fontsize=7)

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS.get(m, m) for m in methods])
    ax.set_ylabel("Δ Score  (English − Hindi)")
    ax.set_title("Hindi–English Retrieval Gap by Method (Δ = EN − HI)\nPositive = English outperforms Hindi",
                 fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    path = out_dir / "fig2_hindi_english_gap.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def fig3_query_level_recall5_distribution(query_df: pd.DataFrame, out_dir: Path):
    """Figure 3: Distribution of per-query Recall@5 across methods and languages."""
    if query_df is None:
        print("Skipping Fig3: query_level_results.csv not found.")
        return
    languages = sorted(query_df["language"].unique())
    methods = [m for m in METHODS_ORDER if m in query_df["method"].unique()]
    n_rows = len(languages)
    fig, axes = plt.subplots(n_rows, len(methods), figsize=(12, 4 * n_rows), squeeze=False)
    for r, lang in enumerate(languages):
        for c, method in enumerate(methods):
            ax = axes[r][c]
            sub = query_df[(query_df["language"] == lang) & (query_df["method"] == method)]
            vals = sub["recall_at_5"].dropna()
            ax.hist(vals, bins=[0, 0.1, 0.5, 1.0, 1.01], edgecolor="black",
                    color=LANG_COLORS.get(lang, "steelblue"), alpha=0.8)
            ax.set_title(f"{LANG_LABELS.get(lang, lang)} / {METHOD_LABELS.get(method, method)}",
                         fontsize=8)
            ax.set_xlabel("Recall@5", fontsize=7)
            ax.set_ylabel("# Queries", fontsize=7)
            ax.set_xlim(-0.05, 1.05)
            mean_val = vals.mean()
            ax.axvline(mean_val, color="red", linestyle="--", linewidth=1.2,
                       label=f"Mean={mean_val:.3f}")
            ax.legend(fontsize=7)

    fig.suptitle("Per-Query Recall@5 Distribution by Language and Method",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    path = out_dir / "fig3_recall5_distributions.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def fig4_failure_rate_summary(query_df: pd.DataFrame, out_dir: Path):
    """Figure 4: Failure rate (MRR@10==0) per method and language."""
    if query_df is None:
        print("Skipping Fig4: query_level_results.csv not found.")
        return
    languages = sorted(query_df["language"].unique())
    methods = [m for m in METHODS_ORDER if m in query_df["method"].unique()]
    data = []
    for lang in languages:
        for method in methods:
            sub = query_df[(query_df["language"] == lang) & (query_df["method"] == method)]
            total = len(sub)
            fails = (sub["reciprocal_rank_at_10"] == 0).sum()
            rate = fails / total if total > 0 else 0.0
            data.append({"language": lang, "method": method, "total": total,
                         "failures": fails, "failure_rate": rate})
    fdf = pd.DataFrame(data)

    x = np.arange(len(methods))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    for li, lang in enumerate(languages):
        sub = fdf[fdf["language"] == lang]
        rates = [float(sub[sub["method"] == m]["failure_rate"].values[0])
                 if not sub[sub["method"] == m].empty else np.nan for m in methods]
        offset = (li - 0.5) * width
        bars = ax.bar(x + offset, [r * 100 for r in rates], width,
                      label=LANG_LABELS.get(lang, lang),
                      color=LANG_COLORS.get(lang, f"C{li}"),
                      alpha=0.85, edgecolor="white")
        for bar, (rate, row) in zip(bars, zip(rates, fdf[fdf["language"] == lang].itertuples())):
            if not np.isnan(rate):
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 0.5,
                        f"{rate*100:.1f}%\n({row.failures}/{row.total})",
                        ha="center", va="bottom", fontsize=7)

    ax.set_xticks(x)
    ax.set_xticklabels([METHOD_LABELS.get(m, m) for m in methods])
    ax.set_ylabel("Failure Rate (%) — No relevant doc in Top 10")
    ax.set_title("Retrieval Failure Rate by Method and Query Language\n(SciFact test set)",
                 fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    path = out_dir / "fig4_failure_rates.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="results")
    parser.add_argument("--output_dir", default="reports/figures")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics, query_df, failures = load_data(results_dir)
    print(f"Loaded metrics: {len(metrics)} rows; languages: {sorted(metrics['language'].unique())}")

    fig1_metric_comparison_bar(metrics, out_dir)
    fig2_hindi_english_gap(metrics, out_dir)
    fig3_query_level_recall5_distribution(query_df, out_dir)
    fig4_failure_rate_summary(query_df, out_dir)

    print(f"\nAll figures saved to {out_dir}/")
    print("Note: These figures are generated from actual experiment output.")


if __name__ == "__main__":
    main()
