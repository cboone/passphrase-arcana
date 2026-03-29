"""Step 2b: Best-effort removal of likely proper nouns.

Scans raw text files (which preserve original capitalization) for words
that appear in lowercase at least once. Words in word_frequencies.csv
that are never seen lowercase are flagged as likely proper nouns and
removed.

Concordance-sourced files (McCarthy, Nabokov) are already entirely
lowercase, so every concordance word passes the filter automatically.
"""

from __future__ import annotations

import csv
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_RAW = ROOT / "data" / "raw"
DATA_WORDS = ROOT / "data" / "words"

LOWERCASE_TOKEN = re.compile(r"\b([a-z]+)\b")


def scan_lowercase_tokens(raw_dir: Path, min_len: int, max_len: int) -> set[str]:
    """Build a set of tokens that appear in lowercase in the raw text files.

    Only tokens within the configured length bounds are included.
    """
    seen: set[str] = set()
    for path in sorted(raw_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in LOWERCASE_TOKEN.finditer(text):
            token = match.group(1)
            if min_len <= len(token) <= max_len:
                seen.add(token)
    return seen


def filter_proper_nouns(
    csv_path: Path,
    seen_lowercase: set[str],
) -> tuple[list[dict], list[str]]:
    """Partition word_frequencies.csv rows into kept and removed.

    Returns (kept_rows, removed_words) where kept_rows is a list of
    CSV row dicts and removed_words is a sorted list of removed words.
    """
    kept: list[dict] = []
    removed: list[str] = []

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["word"] in seen_lowercase:
                kept.append(row)
            else:
                removed.append(row["word"])

    removed.sort()
    return kept, removed


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    min_len = config["general"]["min_word_length"]
    max_len = config["general"]["max_word_length"]
    languages = config["languages"]

    for lang, lang_cfg in languages.items():
        lang_name = lang_cfg["name"]

        raw_dir = DATA_RAW / lang
        if not raw_dir.exists():
            print(f"[{lang_name}] No raw texts found, skipping")
            continue

        words_dir = DATA_WORDS / lang
        csv_path = words_dir / "word_frequencies.csv"
        if not csv_path.exists():
            print(f"[{lang_name}] No word frequencies found, skipping")
            continue

        # Scan raw texts for lowercase tokens
        seen_lowercase = scan_lowercase_tokens(raw_dir, min_len, max_len)

        # Filter the CSV
        kept, removed = filter_proper_nouns(csv_path, seen_lowercase)

        # Rewrite word_frequencies.csv with only kept rows
        with csv_path.open("w", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["word", "count", "num_authors", "original_forms"]
            )
            writer.writeheader()
            writer.writerows(kept)

        # Rewrite all_words.txt to stay consistent
        kept_words = sorted(row["word"] for row in kept)
        (words_dir / "all_words.txt").write_text("\n".join(kept_words) + "\n")

        # Write removed words for inspection
        (words_dir / "proper_nouns_removed.txt").write_text("\n".join(removed) + "\n")

        total = len(kept) + len(removed)
        print(
            f"[{lang_name}] {len(removed)} likely proper nouns removed "
            f"({total} -> {len(kept)} words)"
        )


if __name__ == "__main__":
    main()
