"""Fetch word sources not available on Project Gutenberg.

Handles:
- McCarthy concordance PDF (academic word list from johnsepich.com)
- Nabokov texts from GitHub (bukvik-workshop-corpora, for local processing only)
"""

from __future__ import annotations

import re
import sys
import tomllib
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


def fetch_nabokov_texts(repo: str, files: list[str], dest_dir: Path) -> None:
    """Download Nabokov text files from the bukvik-workshop-corpora GitHub repo."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        for filename in files:
            # Derive a clean dest filename
            slug = filename.split(" - ")[0].lower().replace("-", "_")
            dest = dest_dir / f"nabokov_{slug}.txt"

            if dest.exists() and dest.stat().st_size > 0:
                print(f"  [Nabokov] {slug} (cached)")
                continue

            url = GITHUB_RAW.format(repo=repo, file=filename.replace(" ", "%20"))
            try:
                resp = client.get(url)
                resp.raise_for_status()
                dest.write_text(resp.text, encoding="utf-8")
                print(f"  [Nabokov] {slug} -> {dest.name}")
            except Exception as exc:
                print(f"  [Nabokov] {slug} ERROR: {exc}", file=sys.stderr)


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    external = config.get("languages", {}).get("en", {}).get("external", {})

    if "mccarthy" in external:
        cfg = external["mccarthy"]
        fetch_mccarthy_concordance(cfg["url"], DATA_RAW / "en" / "mccarthy_concordance.txt")

    if "nabokov" in external:
        cfg = external["nabokov"]
        fetch_nabokov_texts(cfg["repo"], cfg["files"], DATA_RAW / "en")


if __name__ == "__main__":
    main()
