"""Step 5: Build the final word list: deduplicate, remove prefix words, output."""

from __future__ import annotations

import math
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_SCORED = ROOT / "data" / "scored"
OUTPUT = ROOT / "output"


def load_scored_words(lang: str) -> list[str]:
    """Load words from the scored TSV, discarding the effort column."""
    path = DATA_SCORED / f"{lang}_scored.tsv"
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    # Skip header
    return [line.split("\t")[0] for line in lines[1:]]


def remove_prefix_words(words: list[str]) -> list[str]:
    """Remove words that are prefixes of other words in the list.

    When a conflict is found, the shorter (prefix) word is removed,
    keeping the longer, more distinctive word.
    """
    word_set = set(words)
    prefixes_to_remove: set[str] = set()

    # Sort by length so we check shorter words as potential prefixes
    sorted_by_len = sorted(word_set, key=len)

    for i, candidate in enumerate(sorted_by_len):
        if candidate in prefixes_to_remove:
            continue
        # Check if this word is a prefix of any longer word
        for j in range(i + 1, len(sorted_by_len)):
            longer = sorted_by_len[j]
            if longer.startswith(candidate):
                prefixes_to_remove.add(candidate)
                break

    return sorted(word_set - prefixes_to_remove)


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    languages = config["languages"]

    # Load words in priority order (en > fr > pt)
    all_words: set[str] = set()
    lang_counts: dict[str, int] = {}
    for lang in languages:
        lang_words = load_scored_words(lang)
        new_words = [w for w in lang_words if w not in all_words]
        all_words.update(new_words)
        lang_counts[lang] = len(new_words)
        lang_name = languages[lang]["name"]
        print(f"[{lang_name}] {len(new_words)} unique words added ({len(lang_words)} before dedup)")

    # Remove prefix words
    word_list = sorted(all_words)
    pre_prefix_count = len(word_list)
    word_list = remove_prefix_words(word_list)
    prefix_removed = pre_prefix_count - len(word_list)

    # Write output
    OUTPUT.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT / "word-list.txt"
    out_path.write_text("\n".join(word_list) + "\n")

    # Statistics
    count = len(word_list)
    entropy = math.log2(count) if count > 0 else 0
    lengths = [len(w) for w in word_list]
    mean_len = sum(lengths) / len(lengths) if lengths else 0

    print(f"\nFinal word list: {out_path}")
    print(f"  Words: {count}")
    print(f"  Entropy per word: {entropy:.2f} bits")
    print(f"  Mean word length: {mean_len:.1f} characters")
    print(f"  Prefix words removed: {prefix_removed}")


if __name__ == "__main__":
    main()
