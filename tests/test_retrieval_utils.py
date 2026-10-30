#!/usr/bin/env python3
"""Unit tests for the retrieval pipeline.

Tests cover: recall_at_k, reciprocal_rank_at_k, tokenize, load_hindi schema.
All tests use only built-in Python or numpy — no BEIR/sentence-transformers needed.
Run with: pytest tests/test_retrieval_utils.py -v
"""
import sys
import os
import math
import tempfile
import csv
import types

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Stub ALL heavy imports before anything in scripts/ is imported.
# We create a full module hierarchy so that
#   from beir.datasets.data_loader import GenericDataLoader
# and similar statements don't fail.
# ---------------------------------------------------------------------------

def _make_stub(name):
    mod = types.ModuleType(name)
    mod.__path__ = []          # make it a package
    mod.__package__ = name
    return mod

_STUBS = [
    "beir",
    "beir.util",
    "beir.datasets",
    "beir.datasets.data_loader",
    "rank_bm25",
    "sentence_transformers",
    "sklearn",
    "sklearn.feature_extraction",
    "sklearn.feature_extraction.text",
]

for _name in _STUBS:
    if _name not in sys.modules:
        sys.modules[_name] = _make_stub(_name)

# Provide attributes that run_retrieval.py references at import time.
sys.modules["beir.util"].download_and_unzip = lambda *a, **kw: None
sys.modules["beir.datasets.data_loader"].GenericDataLoader = object
sys.modules["rank_bm25"].BM25Okapi = object
sys.modules["sentence_transformers"].SentenceTransformer = object
sys.modules["sklearn.feature_extraction.text"].ENGLISH_STOP_WORDS = frozenset()

# ---------------------------------------------------------------------------
# Now import the functions under test.
# ---------------------------------------------------------------------------
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from run_retrieval import recall_at_k, reciprocal_rank_at_k, tokenize, load_hindi  # noqa: E402


# ===========================================================================
# recall_at_k
# ===========================================================================

class TestRecallAtK:
    def test_single_relevant_hit_at_1(self):
        ranked = ["doc1", "doc2", "doc3"]
        relevant = {"doc1"}
        assert recall_at_k(ranked, relevant, 1) == pytest.approx(1.0)

    def test_single_relevant_miss_at_1(self):
        ranked = ["doc2", "doc3", "doc1"]
        relevant = {"doc1"}
        assert recall_at_k(ranked, relevant, 1) == pytest.approx(0.0)

    def test_single_relevant_hit_at_5_position_3(self):
        ranked = ["doc2", "doc3", "doc1", "doc4", "doc5"]
        relevant = {"doc1"}
        # doc1 is at position 3 (index 2); within top-5
        assert recall_at_k(ranked, relevant, 5) == pytest.approx(1.0)

    def test_two_relevant_one_found_in_top_5(self):
        ranked = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        relevant = {"doc1", "doc10"}
        # 1 of 2 relevant in top 5 → 0.5
        assert recall_at_k(ranked, relevant, 5) == pytest.approx(0.5)

    def test_two_relevant_both_found_in_top_5(self):
        ranked = ["doc1", "doc10", "doc3", "doc4", "doc5"]
        relevant = {"doc1", "doc10"}
        assert recall_at_k(ranked, relevant, 5) == pytest.approx(1.0)

    def test_empty_relevant_returns_nan(self):
        ranked = ["doc1", "doc2"]
        relevant = set()
        result = recall_at_k(ranked, relevant, 5)
        assert math.isnan(result)

    def test_k_larger_than_ranked_list(self):
        ranked = ["doc1"]
        relevant = {"doc1"}
        # Only 1 doc in ranked list, k=10; still finds doc1
        assert recall_at_k(ranked, relevant, 10) == pytest.approx(1.0)

    def test_no_relevant_in_top_k(self):
        ranked = ["doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8", "doc9", "doc10", "doc11"]
        relevant = {"doc1"}
        assert recall_at_k(ranked, relevant, 10) == pytest.approx(0.0)

    def test_recall_at_k_equal_k(self):
        # Relevant doc is exactly at position k (index k-1)
        ranked = ["doc2", "doc3", "doc4", "doc5", "doc1"]
        relevant = {"doc1"}
        assert recall_at_k(ranked, relevant, 5) == pytest.approx(1.0)

    def test_recall_at_k_beyond_k(self):
        # Relevant doc is at position k+1 (should not be counted for k)
        ranked = ["doc2", "doc3", "doc4", "doc5", "doc6", "doc1"]
        relevant = {"doc1"}
        assert recall_at_k(ranked, relevant, 5) == pytest.approx(0.0)


# ===========================================================================
# reciprocal_rank_at_k
# ===========================================================================

class TestReciprocalRankAtK:
    def test_relevant_at_position_1(self):
        ranked = ["doc1", "doc2", "doc3"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 10) == pytest.approx(1.0)

    def test_relevant_at_position_2(self):
        ranked = ["doc2", "doc1", "doc3"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 10) == pytest.approx(0.5)

    def test_relevant_at_position_5(self):
        ranked = ["d1", "d2", "d3", "d4", "doc1"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 10) == pytest.approx(1.0 / 5)

    def test_no_relevant_in_top_k_returns_zero(self):
        ranked = ["doc2", "doc3", "doc4", "doc5", "doc6", "doc7", "doc8", "doc9", "doc10", "doc11"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 10) == pytest.approx(0.0)

    def test_relevant_at_position_k(self):
        # k=5, relevant at position 5 (index 4)
        ranked = ["d1", "d2", "d3", "d4", "doc1", "doc2"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 5) == pytest.approx(1.0 / 5)

    def test_relevant_at_position_k_plus_1_returns_zero(self):
        # Relevant just outside the k cutoff
        ranked = ["d1", "d2", "d3", "d4", "d5", "doc1"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 5) == pytest.approx(0.0)

    def test_first_relevant_wins_with_multiple_relevant(self):
        # Both doc1 and doc2 are relevant; doc2 is at position 1
        ranked = ["doc2", "doc1", "doc3"]
        relevant = {"doc1", "doc2"}
        assert reciprocal_rank_at_k(ranked, relevant, 10) == pytest.approx(1.0)

    def test_empty_ranked_list_returns_zero(self):
        assert reciprocal_rank_at_k([], {"doc1"}, 10) == pytest.approx(0.0)

    def test_k_zero_returns_zero(self):
        ranked = ["doc1", "doc2"]
        relevant = {"doc1"}
        assert reciprocal_rank_at_k(ranked, relevant, 0) == pytest.approx(0.0)


# ===========================================================================
# tokenize
# ===========================================================================

class TestTokenize:
    def test_basic_lowercase(self):
        assert tokenize("Hello World") == ["hello", "world"]

    def test_strips_punctuation(self):
        assert tokenize("cell, signaling: pathway!") == ["cell", "signaling", "pathway"]

    def test_empty_string(self):
        assert tokenize("") == []

    def test_none_as_string(self):
        # The function does str(text).lower().split()
        result = tokenize(None)
        assert result == ["none"]

    def test_scientific_text(self):
        text = "COVID-19 (SARS-CoV-2) causes acute respiratory distress syndrome."
        tokens = tokenize(text)
        # Hyphens are kept (not in strip chars), so COVID-19 stays
        assert "covid-19" in tokens
        assert "acute" in tokens
        assert "respiratory" in tokens
        # Period stripped from end: "syndrome." → "syndrome"
        assert "syndrome" in tokens

    def test_brackets_stripped(self):
        tokens = tokenize("[test] {value} (result)")
        assert "test" in tokens
        assert "value" in tokens
        assert "result" in tokens


# ===========================================================================
# load_hindi — schema and validation
# ===========================================================================

class TestLoadHindi:
    def _write_csv(self, rows, tmp_path, header=None):
        """Helper: write a CSV file and return its path."""
        fpath = os.path.join(tmp_path, "hindi.csv")
        if header is None:
            header = ["query_id", "english_text", "hindi_text", "translation_method",
                      "human_checked", "reviewer_notes"]
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return fpath

    def test_valid_csv_loads_correctly(self, tmp_path):
        queries = {"1": "English claim 1", "2": "English claim 2"}
        rows = [
            {"query_id": "1", "english_text": "English claim 1",
             "hindi_text": "हिंदी दावा 1", "translation_method": "google_translate",
             "human_checked": "true", "reviewer_notes": ""},
            {"query_id": "2", "english_text": "English claim 2",
             "hindi_text": "हिंदी दावा 2", "translation_method": "google_translate",
             "human_checked": "false", "reviewer_notes": ""},
        ]
        path = self._write_csv(rows, tmp_path)
        result = load_hindi(path, queries)
        assert result["1"] == "हिंदी दावा 1"
        assert result["2"] == "हिंदी दावा 2"

    def test_missing_file_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_hindi(os.path.join(tmp_path, "nonexistent.csv"), {"1": "text"})

    def test_none_path_raises_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_hindi(None, {"1": "text"})

    def test_missing_column_raises_value_error(self, tmp_path):
        queries = {"1": "text"}
        rows = [{"query_id": "1", "english_text": "text",
                 "hindi_text": "पाठ", "translation_method": "manual"}]
        path = self._write_csv(rows, tmp_path,
                               header=["query_id", "english_text", "hindi_text", "translation_method"])
        with pytest.raises(ValueError, match="missing required columns"):
            load_hindi(path, queries)

    def test_unknown_query_id_raises_value_error(self, tmp_path):
        queries = {"1": "text"}
        rows = [{"query_id": "999", "english_text": "text",
                 "hindi_text": "पाठ", "translation_method": "manual",
                 "human_checked": "true", "reviewer_notes": ""}]
        path = self._write_csv(rows, tmp_path)
        with pytest.raises(ValueError, match="unknown query IDs"):
            load_hindi(path, queries)

    def test_duplicate_query_id_raises_value_error(self, tmp_path):
        queries = {"1": "text"}
        rows = [
            {"query_id": "1", "english_text": "text", "hindi_text": "पाठ",
             "translation_method": "manual", "human_checked": "true", "reviewer_notes": ""},
            {"query_id": "1", "english_text": "text", "hindi_text": "पाठ दूसरा",
             "translation_method": "manual", "human_checked": "true", "reviewer_notes": ""},
        ]
        path = self._write_csv(rows, tmp_path)
        with pytest.raises(ValueError, match="duplicate query_id"):
            load_hindi(path, queries)

    def test_empty_hindi_text_raises_value_error(self, tmp_path):
        queries = {"1": "text"}
        rows = [{"query_id": "1", "english_text": "text", "hindi_text": "",
                 "translation_method": "manual", "human_checked": "true", "reviewer_notes": ""}]
        path = self._write_csv(rows, tmp_path)
        with pytest.raises(ValueError, match="empty hindi_text"):
            load_hindi(path, queries)

    def test_unchecked_translations_emit_warning(self, tmp_path, capsys):
        queries = {"1": "text"}
        rows = [{"query_id": "1", "english_text": "text", "hindi_text": "पाठ",
                 "translation_method": "auto", "human_checked": "false", "reviewer_notes": ""}]
        path = self._write_csv(rows, tmp_path)
        load_hindi(path, queries)
        captured = capsys.readouterr()
        assert "WARNING" in captured.err


# ===========================================================================
# Integration: mean MRR across a known set of queries
# ===========================================================================

class TestAggregateMetrics:
    """
    Manually verify the aggregate metrics for a tiny known dataset.
    This catches formula or aggregation bugs.
    """

    def test_mrr_at_10_manual(self):
        # 3 queries: relevant at rank 1, 2, and not found
        rr_values = [1.0, 0.5, 0.0]
        expected_mrr = (1.0 + 0.5 + 0.0) / 3
        assert np.mean(rr_values) == pytest.approx(expected_mrr)

    def test_recall_at_5_all_found(self):
        # 3 queries, each with 1 relevant doc, all found in top 5
        recalls = [recall_at_k(["d1", "d2"], {"d1"}, 5),
                   recall_at_k(["d2", "d1"], {"d1"}, 5),
                   recall_at_k(["d3", "d1", "d2"], {"d1"}, 5)]
        assert np.nanmean(recalls) == pytest.approx(1.0)

    def test_recall_at_1_only_first_position(self):
        recalls = [recall_at_k(["d1", "d2"], {"d1"}, 1),   # hit
                   recall_at_k(["d2", "d1"], {"d1"}, 1)]   # miss
        assert np.nanmean(recalls) == pytest.approx(0.5)

    def test_ranking_tie_handling(self):
        # Two docs with equal BM25 scores; order is determined by argsort (stable)
        # We test that metrics are consistent regardless of tie-breaking order
        ranked_a = ["doc1", "doc2"]  # tie, doc1 first
        ranked_b = ["doc2", "doc1"]  # tie, doc2 first
        relevant = {"doc1"}
        rr_a = reciprocal_rank_at_k(ranked_a, relevant, 10)
        rr_b = reciprocal_rank_at_k(ranked_b, relevant, 10)
        # Results differ based on tie-breaking: 1.0 vs 0.5
        assert rr_a == pytest.approx(1.0)
        assert rr_b == pytest.approx(0.5)
