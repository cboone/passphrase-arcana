"""Step 3: Validate extracted words against dictionaries."""

from __future__ import annotations

import csv
import tomllib
from pathlib import Path

from spellchecker import SpellChecker
from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_WORDS = ROOT / "data" / "words"
DATA_VALIDATED = ROOT / "data" / "validated"

# Minimum number of distinct authors for the multi-author heuristic
MIN_AUTHORS_HEURISTIC = 3


def load_word_data(lang: str) -> dict[str, dict]:
    """Load word frequency data from the extract step's CSV."""
    csv_path = DATA_WORDS / lang / "word_frequencies.csv"
    data: dict[str, dict] = {}
    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            originals = set(row["original_forms"].split("|")) if row["original_forms"] else set()
            data[row["word"]] = {
                "count": int(row["count"]),
                "num_authors": int(row["num_authors"]),
                "originals": originals,
            }
    return data


def validate_word(
    word: str,
    originals: set[str],
    num_authors: int,
    count: int,
    lang: str,
    spell: SpellChecker,
) -> bool:
    """Check if a word passes any validation tier."""
    # Tier 1: wordfreq (try original accented forms for fr/pt)
    # Require zipf >= 2.0 to filter out extremely rare words, foreign words,
    # and misspellings that appear in wordfreq's multi-language corpus.
    # For single-author, single-occurrence words, require zipf >= 2.5 to
    # filter the low-quality tail of barely-passing foreign words and names.
    min_zipf = 2.5 if (num_authors == 1 and count == 1) else 2.0
    forms_to_check = originals | {word}
    for form in forms_to_check:
        if zipf_frequency(form, lang) >= min_zipf:
            return True

    # Tier 2: pyspellchecker
    if spell.known([word]):
        return True
    for form in originals:
        if spell.known([form]):
            return True

    # Tier 3: multi-author heuristic
    if num_authors >= MIN_AUTHORS_HEURISTIC:
        return True

    return False


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    languages = config["languages"]

    DATA_VALIDATED.mkdir(parents=True, exist_ok=True)

    for lang, lang_cfg in languages.items():
        lang_name = lang_cfg["name"]

        words_file = DATA_WORDS / lang / "all_words.txt"
        if not words_file.exists():
            print(f"[{lang_name}] No extracted words found, skipping")
            continue

        word_data = load_word_data(lang)

        # pyspellchecker supports en, fr, pt among others
        spell = SpellChecker(language=lang)

        validated = []
        rejected = []

        for word, data in word_data.items():
            if validate_word(word, data["originals"], data["num_authors"], data["count"], lang, spell):
                validated.append(word)
            else:
                rejected.append(word)

        validated.sort()
        rejected.sort()

        (DATA_VALIDATED / f"{lang}_validated.txt").write_text("\n".join(validated) + "\n")
        (DATA_VALIDATED / f"{lang}_rejected.txt").write_text("\n".join(rejected) + "\n")

        print(
            f"[{lang_name}] {len(validated)} validated, {len(rejected)} rejected "
            f"({len(rejected) / max(len(word_data), 1) * 100:.1f}% rejection rate)"
        )


if __name__ == "__main__":
    main()
