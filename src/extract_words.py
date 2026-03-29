"""Step 2: Extract words from raw texts, strip diacritics, filter by length."""

from __future__ import annotations

import csv
import re
import tomllib
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_RAW = ROOT / "data" / "raw"
DATA_WORDS = ROOT / "data" / "words"

WORD_PATTERN = re.compile(r"[a-z]+")


def strip_diacritics(text: str) -> str:
    """Remove diacritical marks, producing ASCII-only lowercase text."""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")


def extract_from_file(
    path: Path,
    min_len: int,
    max_len: int,
    needs_diacritics_strip: bool,
) -> dict[str, tuple[int, set[str]]]:
    """Extract words from a single text file.

    Returns dict mapping word -> (count, set of original accented forms).
    The accented forms are kept for dictionary validation of French/Portuguese words.
    """
    text = path.read_text(encoding="utf-8", errors="replace")
    text_lower = text.lower()

    if needs_diacritics_strip:
        # Keep the original accented tokens for later validation lookups
        accented_tokens = WORD_PATTERN.findall(strip_diacritics(text_lower).replace("'", " "))
        # Also extract the original forms before stripping
        original_tokens = re.findall(r"[a-zA-Z\u00C0-\u024F]+", text_lower)
        stripped_to_original: dict[str, set[str]] = defaultdict(set)
        for orig in original_tokens:
            stripped = strip_diacritics(orig)
            stripped_ascii = "".join(c for c in stripped if c.isascii() and c.isalpha())
            if stripped_ascii:
                stripped_to_original[stripped_ascii].add(orig)
        tokens = accented_tokens
    else:
        tokens = WORD_PATTERN.findall(text_lower)
        stripped_to_original = {}

    result: dict[str, tuple[int, set[str]]] = {}
    for token in tokens:
        if min_len <= len(token) <= max_len:
            if token in result:
                count, originals = result[token]
                result[token] = (count + 1, originals)
            else:
                originals = stripped_to_original.get(token, {token})
                result[token] = (1, originals)
    return result


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    min_len = config["general"]["min_word_length"]
    max_len = config["general"]["max_word_length"]
    languages = config["languages"]

    for lang, lang_cfg in languages.items():
        lang_name = lang_cfg["name"]
        needs_strip = lang in ("fr", "pt")
        sources = lang_cfg.get("sources", {})

        # word -> {total_count, set_of_authors, set_of_original_forms}
        word_data: dict[str, dict] = {}

        def process_author(author: str, paths: list[Path]) -> None:
            """Process all text files for a single author."""
            author_words: set[str] = set()
            for path in paths:
                if not path.exists():
                    continue
                file_words = extract_from_file(path, min_len, max_len, needs_strip)
                for word, (count, originals) in file_words.items():
                    if word not in word_data:
                        word_data[word] = {
                            "count": 0,
                            "authors": set(),
                            "originals": set(),
                        }
                    word_data[word]["count"] += count
                    word_data[word]["originals"].update(originals)
                    author_words.add(word)
            for w in author_words:
                word_data[w]["authors"].add(author)

        # Gutenberg sources
        for author, ebook_ids in sources.items():
            paths = [DATA_RAW / lang / f"{author}_{ebook_id}.txt" for ebook_id in ebook_ids]
            process_author(author, paths)

        # External sources (concordances, GitHub corpora, etc.)
        external = lang_cfg.get("external", {})
        for author in external:
            # Find all files matching {author}_*.txt in the raw directory
            paths = sorted((DATA_RAW / lang).glob(f"{author}_*.txt"))
            process_author(author, paths)

        # Write outputs
        out_dir = DATA_WORDS / lang
        out_dir.mkdir(parents=True, exist_ok=True)

        words_sorted = sorted(word_data.keys())
        (out_dir / "all_words.txt").write_text("\n".join(words_sorted) + "\n")

        with (out_dir / "word_frequencies.csv").open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["word", "count", "num_authors", "original_forms"])
            for word in words_sorted:
                d = word_data[word]
                originals_str = "|".join(sorted(d["originals"]))
                writer.writerow([word, d["count"], len(d["authors"]), originals_str])

        print(f"[{lang_name}] {len(words_sorted)} unique words extracted")


if __name__ == "__main__":
    main()
