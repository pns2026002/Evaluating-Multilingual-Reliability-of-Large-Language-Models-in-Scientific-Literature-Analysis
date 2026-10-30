#!/usr/bin/env python3
"""Fill remaining untranslated queries using local MarianMT model.

Runs 100% offline using already-cached Helsinki-NLP/opus-mt-en-hi.
Uses greedy decoding (num_beams=1) for fast CPU throughput.
"""
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pandas as pd
from transformers import MarianMTModel, MarianTokenizer

def main():
    csv_path = Path("data/hindi_queries.csv")
    df = pd.read_csv(csv_path, dtype={"query_id": str})
    print(f"Loaded {len(df)} rows from {csv_path}")

    needs_trans = (
        df["hindi_text"].isna()
        | df["hindi_text"].str.contains("TRANSLATION", na=False)
        | (df["hindi_text"].str.strip() == "")
    )
    missing_indices = df[needs_trans].index.tolist()
    print(f"Missing/failed rows: {len(missing_indices)} / {len(df)}")

    if not missing_indices:
        print("All queries already translated!")
        return

    print("Loading local MarianMT model Helsinki-NLP/opus-mt-en-hi...")
    model_name = "Helsinki-NLP/opus-mt-en-hi"
    tokenizer = MarianTokenizer.from_pretrained(model_name, local_files_only=True)
    model = MarianMTModel.from_pretrained(model_name, local_files_only=True)
    model.eval()

    batch_size = 8
    t0 = time.time()
    for b in range(0, len(missing_indices), batch_size):
        b_idx = missing_indices[b:b + batch_size]
        texts = [df.loc[i, "english_text"] for i in b_idx]
        tokens = tokenizer(texts, return_tensors="pt", padding=True, truncation=True, max_length=128)
        gen = model.generate(**tokens, num_beams=1, max_new_tokens=64)
        translations = [tokenizer.decode(g, skip_special_tokens=True) for g in gen]

        for idx, trans in zip(b_idx, translations):
            df.loc[idx, "hindi_text"] = trans
            df.loc[idx, "translation_method"] = "opus_mt_en_hi"

        # Checkpoint to disk after every batch
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        elapsed = time.time() - t0
        done = b + len(b_idx)
        print(f"  [{done}/{len(missing_indices)}] translated ({elapsed:.1f}s elapsed, {elapsed/done:.2f}s/query)", flush=True)

    print(f"\nCompleted in {time.time() - t0:.1f}s. Saved to {csv_path}")

    # Final check
    df_check = pd.read_csv(csv_path, dtype={"query_id": str})
    assert len(df_check) == 300
    assert not df_check["hindi_text"].isna().any()
    assert not df_check["hindi_text"].str.contains("TRANSLATION").any()
    print("ALL 300 QUERIES ARE VALID AND TRANSLATED!")
    print(df_check["translation_method"].value_counts())

if __name__ == "__main__":
    main()
