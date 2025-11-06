
# prep_truthfulqa.py
# REQUIRE: pip install datasets pandas
import argparse
import random
import sys
from typing import List, Any

import pandas as pd
from datasets import load_dataset

def pick_answer(row: dict) -> str:
    """Prefer 'best_answer' if present; otherwise first non-empty from 'correct_answers'."""
    if isinstance(row.get("best_answer"), str) and row["best_answer"].strip():
        return row["best_answer"].strip()
    ca = row.get("correct_answers")
    if isinstance(ca, (list, tuple)) and ca:
        for ans in ca:
            if isinstance(ans, str) and ans.strip():
                return ans.strip()
    return ""

def main():
    ap = argparse.ArgumentParser(description="Prepare TruthfulQA into questions_*.csv (question,ground_truth).")
    ap.add_argument("--name", default="domenicrosati/TruthfulQA", help="HF dataset name/path")
    ap.add_argument("--split", default=None, help="Split name (auto if omitted)")
    ap.add_argument("--out", default="truthfulqa_all.csv", help="Output CSV path")
    ap.add_argument("--sample_n", type=int, default=0, help="If >0, sample N rows (deterministic)")
    ap.add_argument("--seed", type=int, default=42, help="Sampling seed")
    args = ap.parse_args()

    # Load dataset (auto split detection if needed)
    try:
        ds = load_dataset(args.name, split=args.split) if args.split else load_dataset(args.name)
    except Exception as e:
        print(f"[ERROR] Cannot load dataset {args.name}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.split is None:
        if isinstance(ds, dict):
            for k in ["validation", "test", "train", "main", "default"]:
                if k in ds:
                    data = ds[k]
                    split_name = k
                    break
            else:
                split_name, data = next(iter(ds.items()))
        else:
            data = ds
            split_name = "unknown"
    else:
        data = ds
        split_name = args.split

    rows = []
    for ex in data:
        q = ex.get("question") or ex.get("Question") or ex.get("prompt") or ""
        if isinstance(q, list):
            q = " ".join([str(t) for t in q])
        q = str(q).strip()
        if not q:
            continue
        gt = pick_answer(ex)
        rows.append({"question": q, "ground_truth": gt})

    df = pd.DataFrame(rows)
    df = df[df["question"].str.len() > 0].copy()
    df = df.drop_duplicates(subset=["question"]).reset_index(drop=True)

    if args.sample_n and 0 < args.sample_n < len(df):
        df = df.sample(n=args.sample_n, random_state=args.seed).reset_index(drop=True)

    df.to_csv(args.out, index=False, encoding="utf-8")
    print(f"[OK] Split: {split_name} | Rows: {len(df)} | Saved: {args.out}")

if __name__ == "__main__":
    main()
