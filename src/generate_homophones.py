"""Generate a homophones CSV from the CMU Pronouncing Dictionary.

One-time generation script. The resulting CSV is committed to the repo
and used by tidy's --homophones flag during the build step.

Each line contains words that share the same pronunciation, separated by
commas. Stress markers are stripped so that words differing only in
stress are treated as homophones.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import httpx

CMU_DICT_URL = "https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict"
ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "homophones.csv"


def fetch_cmu_dict() -> str:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(CMU_DICT_URL)
        resp.raise_for_status()
        return resp.text


def parse_homophones(text: str) -> list[list[str]]:
    """Parse the CMU dict and group words by pronunciation."""
    pron_to_words: dict[str, set[str]] = defaultdict(set)

    for line in text.strip().splitlines():
        if line.startswith(";;;"):
            continue
        parts = line.split()
        word = parts[0].lower()
        # Strip variant markers like word(2)
        if "(" in word:
            word = word[: word.index("(")]
        # Strip stress markers (digits) from phonemes
        phonemes = " ".join(p.rstrip("012") for p in parts[1:])
        pron_to_words[phonemes].add(word)

    # Keep only groups with 2+ distinct words
    return [sorted(words) for words in pron_to_words.values() if len(words) >= 2]


def main() -> None:
    print("Downloading CMU Pronouncing Dictionary...")
    text = fetch_cmu_dict()

    groups = parse_homophones(text)
    groups.sort()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w") as f:
        for group in groups:
            f.write(",".join(group) + "\n")

    total_words = sum(len(g) for g in groups)
    print(f"Wrote {len(groups)} homophone groups ({total_words} words) to {OUTPUT}")


if __name__ == "__main__":
    main()
