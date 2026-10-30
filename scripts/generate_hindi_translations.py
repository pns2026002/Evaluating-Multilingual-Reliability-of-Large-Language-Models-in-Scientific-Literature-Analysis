#!/usr/bin/env python3
"""
Generate draft Hindi translations for SciFact test queries.

IMPORTANT: These translations are MACHINE-GENERATED using deep_translator
(Google Translate API). They are NOT human-reviewed.
All rows are marked human_checked=false until a bilingual reviewer confirms them.

Usage:
    pip install deep_translator
    python scripts/generate_hindi_translations.py \
        --data_dir data/beir \
        --output data/hindi_queries.csv

Prerequisites: The SciFact dataset must already be downloaded (run
run_retrieval.py once with --languages en to trigger the download).

Translation provenance is recorded in each row.
"""
import argparse
import sys
import time
from pathlib import Path

# Ensure UTF-8 output on Windows console (handles Greek letters like alpha, beta, etc.)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd

try:
    from beir.datasets.data_loader import GenericDataLoader
except ImportError:
    print("ERROR: beir not installed. Run: pip install beir>=2.0.0", file=sys.stderr)
    sys.exit(1)

try:
    from deep_translator import GoogleTranslator, MyMemoryTranslator
    _TRANSLATOR_AVAILABLE = True
except ImportError:
    _TRANSLATOR_AVAILABLE = False
    print("WARNING: deep_translator not installed. Will output skeleton CSV only.")
    print("         Install with: pip install deep-translator")


def translate_to_hindi(text: str, retries: int = 2, delay: float = 0.5) -> tuple[str, str]:
    """Translate English text to Hindi using MyMemoryTranslator or GoogleTranslator.
    Returns (hindi_text, method_used).
    """
    if not _TRANSLATOR_AVAILABLE:
        return "[TRANSLATION_PENDING]", "none"

    # Try MyMemoryTranslator first as it has proven reliable
    for attempt in range(retries):
        try:
            translator = MyMemoryTranslator(source="en-US", target="hi-IN")
            result = translator.translate(text)
            if result and result.strip() and not result.startswith("MYMEMORY WARNING"):
                return result.strip(), "mymemory_via_deep_translator"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)

    # Fallback to GoogleTranslator
    for attempt in range(retries):
        try:
            translator = GoogleTranslator(source="en", target="hi")
            result = translator.translate(text)
            if result and result.strip():
                return result.strip(), "google_translate_via_deep_translator"
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay * 2)

    return "[TRANSLATION_FAILED]", "failed"


def main():
    parser = argparse.ArgumentParser(description="Generate Hindi query translations for SciFact.")
    parser.add_argument("--data_dir", default="data/beir")
    parser.add_argument("--output", default="data/hindi_queries.csv")
    parser.add_argument("--limit", type=int, default=0,
                        help="Translate only first N queries (0 = all; use for testing)")
    parser.add_argument("--dry_run", action="store_true",
                        help="Output skeleton CSV without calling translation API")
    args = parser.parse_args()

    dataset_path = Path(args.data_dir) / "scifact"
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}. Run run_retrieval.py --languages en first.", file=sys.stderr)
        sys.exit(1)

    print("Loading SciFact queries...", flush=True)
    _, queries, _ = GenericDataLoader(data_folder=str(dataset_path)).load(split="test")
    queries = {str(k): str(v) for k, v in queries.items()}

    query_ids = sorted(queries.keys(), key=lambda x: int(x) if x.isdigit() else x)
    if args.limit > 0:
        query_ids = query_ids[:args.limit]

    print(f"Translating {len(query_ids)} queries to Hindi...", flush=True)
    if args.dry_run or not _TRANSLATOR_AVAILABLE:
        print("DRY RUN: Generating skeleton CSV only (no API calls).", flush=True)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Check for existing translations to resume without re-translating
    existing_translations = {}
    if out_path.exists():
        try:
            old_df = pd.read_csv(out_path, dtype={"query_id": str})
            for _, r in old_df.iterrows():
                if pd.notna(r.get("hindi_text")) and str(r.get("hindi_text")).strip() not in {"", "[TRANSLATION_FAILED]", "[TRANSLATION_PENDING]"}:
                    existing_translations[str(r["query_id"])] = (str(r["hindi_text"]), str(r.get("translation_method", "mymemory_via_deep_translator")))
            print(f"Resuming: found {len(existing_translations)} existing valid translations in {out_path}", flush=True)
        except Exception as e:
            print(f"Could not load existing translations: {e}", flush=True)

    import concurrent.futures

    to_translate = [qid for qid in query_ids if qid not in existing_translations]
    print(f"Need to translate {len(to_translate)} queries ({len(existing_translations)} already cached in {out_path})", flush=True)

    def _worker(qid):
        text = queries[qid]
        if args.dry_run or not _TRANSLATOR_AVAILABLE:
            return qid, "[TRANSLATION_PENDING]", "pending"
        h, m = translate_to_hindi(text)
        return qid, h, m

    batch_size = 16
    for b_idx in range(0, len(to_translate), batch_size):
        batch_qids = to_translate[b_idx:b_idx + batch_size]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
            futures = {ex.submit(_worker, q): q for q in batch_qids}
            for fut in concurrent.futures.as_completed(futures):
                qid, h, m = fut.result()
                existing_translations[qid] = (h, m)
                print(f"  [{len(existing_translations)}/{len(query_ids)}] Translated query {qid}", flush=True)

        # Save checkpoint after each parallel batch
        rows = []
        for qid in query_ids:
            if qid in existing_translations:
                h, m = existing_translations[qid]
            else:
                h, m = "[TRANSLATION_PENDING]", "pending"
            rows.append({
                "query_id": qid,
                "english_text": queries[qid],
                "hindi_text": h,
                "translation_method": m,
                "human_checked": "false",
                "reviewer_notes": "AUTO-GENERATED — not human-reviewed. Verify scientific terminology."
            })
        pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8-sig")

    rows = []
    for qid in query_ids:
        h, m = existing_translations.get(qid, ("[TRANSLATION_PENDING]", "pending"))
        rows.append({
            "query_id": qid,
            "english_text": queries[qid],
            "hindi_text": h,
            "translation_method": m,
            "human_checked": "false",
            "reviewer_notes": "AUTO-GENERATED — not human-reviewed. Verify scientific terminology."
        })
    df = pd.DataFrame(rows)
    df.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\nSaved {len(rows)} rows to {out_path}")
    print(f"WARNING: All translations are machine-generated and NOT human-reviewed.")
    print(f"         Set human_checked=true only after bilingual review of each row.")
    print(f"         Mark TRANSLATION_PENDING rows in reviewer_notes if translation failed.")


if __name__ == "__main__":
    main()
