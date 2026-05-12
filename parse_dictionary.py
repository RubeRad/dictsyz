"""
parse_dictionary.py

Parses a plain-text English dictionary (one entry per line, format:
    Word (pos.) Definition text.
) into a Python dict where:
    key   = the headword (lowercased)
    value = sorted list of unique lemmatized words from all its definitions

Saves output as both pickle and JSON.

Requirements:
    pip install nltk
    python -c "import nltk; nltk.download('wordnet'); nltk.download('averaged_perceptron_tagger_eng'); nltk.download('punkt_tab')"
"""

import re
import pickle
import json
import string
from collections import defaultdict

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

# ---------------------------------------------------------------------------
# NLTK setup — download quietly if not already present
# ---------------------------------------------------------------------------
for resource in ("wordnet", "averaged_perceptron_tagger_eng", "punkt_tab", "omw-1.4"):
    try:
        nltk.data.find(f"corpora/{resource}" if resource != "averaged_perceptron_tagger_eng" else f"taggers/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

lemmatizer = WordNetLemmatizer()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# POS tag → WordNet POS constant (for accurate lemmatization)
_POS_MAP = {
    "J": wordnet.ADJ,
    "V": wordnet.VERB,
    "N": wordnet.NOUN,
    "R": wordnet.ADV,
}

def _wn_pos(treebank_tag: str) -> str:
    """Map a Penn Treebank POS tag to a WordNet POS tag."""
    return _POS_MAP.get(treebank_tag[0], wordnet.NOUN)


def lemmatize_words(text: str) -> list[str]:
    """
    Tokenize *text*, POS-tag each token, lemmatize, lowercase, and return
    only alphabetic tokens (no punctuation, numbers, or single letters).
    """
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
    result = []
    for word, tag in tagged:
        if not word.isalpha() or len(word) < 2:
            continue
        lemma = lemmatizer.lemmatize(word.lower(), _wn_pos(tag))
        result.append(lemma)
    return result


# Matches the grammatical code at the start of a definition, e.g. "(n.)" or "(n. pl.)"
_POS_RE = re.compile(r"^\s*\([^)]*\)\s*")


def parse_definition_text(raw_def: str) -> list[str]:
    """
    Strip leading POS tag (in parentheses) from *raw_def* and return
    lemmatized words.
    """
    cleaned = _POS_RE.sub("", raw_def)
    return lemmatize_words(cleaned)


# Matches a dictionary entry line:
#   Word  (pos.)  Definition ...
# The headword may contain spaces (e.g. "A fortiori") but not parentheses.
_ENTRY_RE = re.compile(r"^([A-Za-z][A-Za-z\s'-]*?)\s+(\(.*)")


def parse_line(line: str) -> tuple[str, str] | None:
    """
    Return (headword, raw_definition_with_pos_tag) or None if the line
    doesn't look like a dictionary entry.
    """
    line = line.strip()
    if not line:
        return None
    m = _ENTRY_RE.match(line)
    if not m:
        return None
    headword = m.group(1).strip().lower()
    rest = m.group(2)  # everything from the first '(' onward
    return headword, rest


# ---------------------------------------------------------------------------
# Main parser
# ---------------------------------------------------------------------------

def parse_dictionary(filepath: str) -> dict[str, list[str]]:
    """
    Read *filepath* (one entry per line) and return a dict mapping each
    headword to a sorted list of unique lemmatized definition words.
    Multiple lines for the same headword are merged.
    """
    accumulator: defaultdict[str, set[str]] = defaultdict(set)

    with open(filepath, encoding="utf-8", errors="replace") as fh:
        for lineno, line in enumerate(fh, 1):
            parsed = parse_line(line)
            if parsed is None:
                continue
            headword, raw_def = parsed
            words = parse_definition_text(raw_def)
            accumulator[headword].update(words)

    # Convert sets → sorted lists for deterministic output
    return {word: sorted(def_words) for word, def_words in sorted(accumulator.items())}


# ---------------------------------------------------------------------------
# Save / load helpers
# ---------------------------------------------------------------------------

def save_pickle(dictionary: dict, path: str) -> None:
    with open(path, "wb") as fh:
        pickle.dump(dictionary, fh, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"Saved pickle → {path}")


def load_pickle(path: str) -> dict:
    with open(path, "rb") as fh:
        return pickle.load(fh)


def save_json(dictionary: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(dictionary, fh, ensure_ascii=False, indent=2)
    print(f"Saved JSON  → {path}")


def load_json(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import os

    # Accept an optional path argument; default to "dictionary.txt" alongside script
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        src = os.path.join(os.path.dirname(__file__), "dictionary.txt")

    if not os.path.exists(src):
        print(f"Error: source file not found: {src}")
        print("Usage: python parse_dictionary.py [path/to/dictionary.txt]")
        sys.exit(1)

    print(f"Parsing {src} …")
    d = parse_dictionary(src)
    print(f"Parsed {len(d):,} headwords.")

    base = os.path.splitext(src)[0]
    save_pickle(d, base + "_parsed.pkl")
    save_json(d,    base + "_parsed.json")

    # Quick sanity check on the sample entries
    sample_keys = ["accidentally", "accipiter", "accipitres"]
    print("\nSample output:")
    for k in sample_keys:
        if k in d:
            print(f"  {k!r}: {d[k]}")
