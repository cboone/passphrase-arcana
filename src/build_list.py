"""Step 6: Build the final word list using tidy for Schlinkert pruning."""

from __future__ import annotations

import math
import subprocess
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
BLOCKLIST = ROOT / "blocklist.txt"
HOMOPHONES = ROOT / "data" / "homophones.csv"
ARCHAIC_REJECTS = ROOT / "data" / "archaic_rejects.txt"
CONTRACTIONS_REJECTS = ROOT / "data" / "contractions_rejects.txt"
DATA_SCORED = ROOT / "data" / "scored"
TIDY = Path.home() / ".cargo" / "bin" / "tidy"


def load_scored_words(lang: str) -> list[str]:
    """Load words from the scored TSV, discarding the effort column."""
    path = DATA_SCORED / f"{lang}_scored.tsv"
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    return [line.split("\t")[0] for line in lines[1:]]


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    languages = config["languages"]

    # Load words in priority order (en > fr > pt), dedup across languages
    all_words: list[str] = []
    seen: set[str] = set()
    for lang in languages:
        lang_words = load_scored_words(lang)
        new_words = [w for w in lang_words if w not in seen]
        seen.update(new_words)
        all_words.extend(new_words)
        lang_name = languages[lang]["name"]
        print(f"[{lang_name}] {len(new_words)} unique words added ({len(lang_words)} before dedup)")

    # Write temporary word list for tidy
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp.write("\n".join(all_words) + "\n")
        tmp_path = tmp.name

    # Build tidy command
    out_path = ROOT / "passphrase-arcana.txt"
    cmd = [
        str(TIDY),
        "-K",  # Schlinkert pruning (Sardinas-Patterson unique decodability)
        "-AAAA",  # Print full attributes
        "-f",  # Force overwrite output
        "-o",
        str(out_path),
    ]

    # Add reject lists
    if BLOCKLIST.exists():
        cmd.extend(["-r", str(BLOCKLIST)])
    if ARCHAIC_REJECTS.exists():
        cmd.extend(["-r", str(ARCHAIC_REJECTS)])
    if CONTRACTIONS_REJECTS.exists():
        cmd.extend(["-r", str(CONTRACTIONS_REJECTS)])

    # Add homophones
    if HOMOPHONES.exists():
        cmd.extend(["--homophones", str(HOMOPHONES)])

    cmd.append(tmp_path)

    # Run tidy
    print("\nRunning tidy (Schlinkert pruning)...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Clean up temp file
    Path(tmp_path).unlink()

    # Print tidy output (attributes go to stderr)
    if result.stderr:
        print(result.stderr.rstrip())
    if result.returncode != 0:
        print(f"tidy exited with code {result.returncode}")
        if result.stdout:
            print(result.stdout)
        return

    # Print our own statistics
    word_list = out_path.read_text().strip().splitlines()
    count = len(word_list)
    entropy = math.log2(count) if count > 0 else 0
    lengths = [len(w) for w in word_list]
    mean_len = sum(lengths) / len(lengths) if lengths else 0

    print(f"\nFinal word list: {out_path}")
    print(f"  Words: {count}")
    print(f"  Entropy per word: {entropy:.2f} bits")
    print(f"  Mean word length: {mean_len:.1f} characters")
    print(f"  Input words: {len(all_words)}")
    print(f"  Removed by tidy: {len(all_words) - count}")


if __name__ == "__main__":
    main()
