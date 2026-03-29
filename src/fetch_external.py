"""Fetch word sources not available on Project Gutenberg.

Handles:
- McCarthy concordance PDF (academic word list from johnsepich.com)
- Nabokov concordance built from bukvik-workshop-corpora GitHub texts
  (full texts are downloaded temporarily, only the concordance is kept)
"""

from __future__ import annotations

import re
import sys
import tempfile
import tomllib
from collections import Counter
from pathlib import Path

import httpx
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_RAW = ROOT / "data" / "raw"

GITHUB_RAW = "https://raw.githubusercontent.com/{repo}/master/{file}"


def fetch_mccarthy_concordance(url: str, dest: Path) -> None:
    """Download the McCarthy concordance PDF and extract the word list.

    The PDF format is: word [book#][freq], [book#][freq]...
    We extract just the words and write them as plain text (one per line,
    repeated by total frequency) so the existing extract pipeline can
    process them.
    """
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [McCarthy] concordance (cached)")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)

    print(f"  [McCarthy] downloading concordance PDF...")
    with httpx.Client(follow_redirects=True, timeout=60.0) as client:
        resp = client.get(url)
        resp.raise_for_status()

    pdf_bytes = resp.content
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Pattern: word at line start, followed by book/freq data like "1[23], 4[5]"
    # Words can contain hyphens and apostrophes in the concordance
    entry_pattern = re.compile(r"^([a-zA-Z][a-zA-Z'-]*)\s+\d+\[")
    freq_pattern = re.compile(r"\[(\d+)\]")

    words: list[str] = []
    for page in doc:
        text = page.get_text()
        for line in text.splitlines():
            line = line.strip()
            match = entry_pattern.match(line)
            if match:
                word = match.group(1).lower().replace("'", "").replace("-", "")
                if word.isalpha():
                    # Sum frequencies across all books for this word
                    total_freq = sum(int(f) for f in freq_pattern.findall(line))
                    # Repeat word by frequency so extract_words sees realistic counts
                    words.extend([word] * max(total_freq, 1))

    doc.close()

    dest.write_text(" ".join(words), encoding="utf-8")
    unique = len(set(words))
    print(f"  [McCarthy] {unique} unique words extracted from concordance")


def build_nabokov_concordance(repo: str, files: list[str], dest: Path) -> None:
    """Download Nabokov texts temporarily, build a concordance, discard the texts.

    The full copyrighted texts are never stored on disk permanently. Only the
    resulting word frequency concordance is saved, which is non-copyrightable
    factual data (which words appear and how often).
    """
    if dest.exists() and dest.stat().st_size > 0:
        print("  [Nabokov] concordance (cached)")
        return

    dest.parent.mkdir(parents=True, exist_ok=True)
    word_counts: Counter[str] = Counter()
    fetched = 0

    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        for filename in files:
            slug = filename.split(" - ")[0]
            url = GITHUB_RAW.format(repo=repo, file=filename.replace(" ", "%20"))
            try:
                resp = client.get(url)
                resp.raise_for_status()
                # Extract words directly from response text, never saving the full text
                text_lower = resp.text.lower()
                words = re.findall(r"[a-z]+", text_lower)
                word_counts.update(words)
                fetched += 1
                print(f"  [Nabokov] {slug} processed")
            except Exception as exc:
                print(f"  [Nabokov] {slug} ERROR: {exc}", file=sys.stderr)

    # Write concordance: repeat each word by frequency so extract_words
    # sees realistic counts (same format as McCarthy concordance)
    all_words: list[str] = []
    for word, count in word_counts.items():
        all_words.extend([word] * count)

    dest.write_text(" ".join(all_words), encoding="utf-8")
    print(f"  [Nabokov] {len(word_counts)} unique words from {fetched} texts")


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    external = config.get("languages", {}).get("en", {}).get("external", {})

    if "mccarthy" in external:
        cfg = external["mccarthy"]
        fetch_mccarthy_concordance(cfg["url"], DATA_RAW / "en" / "mccarthy_concordance.txt")

    if "nabokov" in external:
        cfg = external["nabokov"]
        build_nabokov_concordance(cfg["repo"], cfg["files"], DATA_RAW / "en" / "nabokov_concordance.txt")


if __name__ == "__main__":
    main()
