"""
assess_dictionary.py

Loads the parsed dictionary (pickle or JSON) and finds all lemmatized words
appearing in definition wordlists that are NOT themselves headword keys.
Ranks them by number of occurrences (descending).

Usage:
    python assess_dictionary.py [path/to/dictionary_parsed.pkl]
    python assess_dictionary.py [path/to/dictionary_parsed.json]

Defaults to looking for dictionary_parsed.pkl alongside the script.
"""

import sys
import os
import pickle
import json
from collections import Counter


def load(path: str) -> dict:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pkl":
        with open(path, "rb") as f:
            return pickle.load(f)
    elif ext == ".json":
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    else:
        raise ValueError(f"Unrecognised file extension: {ext} (expected .pkl or .json)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        src = os.path.join(os.path.dirname(__file__), "dictionary_parsed.pkl")

    if not os.path.exists(src):
        print(f"Error: file not found: {src}")
        sys.exit(1)

    d = load(src)
    print(f"Loaded {len(d):,} headwords from {src}\n")

    headwords = set(d.keys())
    missing: Counter = Counter()

    for headword, def_words in d.items():
        for word in def_words:
            if word not in headwords:
                missing[word] += 1

    total_missing_tokens = sum(missing.values())
    unique_missing = len(missing)

    print(f"Unique words in definitions not found as headwords: {unique_missing:,}")
    print(f"Total occurrences of such words across all definitions: {total_missing_tokens:,}")
    print()
    print(f"{'Rank':<6} {'Word':<30} {'Occurrences':>11}")
    print("-" * 50)
    for rank, (word, count) in enumerate(missing.most_common(), 1):
        print(f"{rank:<6} {word:<30} {count:>11}")
