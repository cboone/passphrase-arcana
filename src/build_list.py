"""Step 6: Build the final word list using tidy for Schlinkert pruning."""

from __future__ import annotations

import json
import math
import re
import statistics
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
STATS_PATH = ROOT / "docs" / "stats.json"
TIDY = Path.home() / ".cargo" / "bin" / "tidy"


def load_scored_words(lang: str) -> list[str]:
    """Load words from the scored TSV, discarding the effort column."""
    path = DATA_SCORED / f"{lang}_scored.tsv"
    if not path.exists():
        return []
    lines = path.read_text().strip().splitlines()
    return [line.split("\t")[0] for line in lines[1:]]


def load_typing_scores(word_set: set[str]) -> list[float]:
    """Load typing effort scores for words in the final list."""
    scores = []
    for lang_dir in DATA_SCORED.iterdir():
        if not lang_dir.name.endswith("_scored.tsv"):
            continue
        lines = lang_dir.read_text().strip().splitlines()
        for line in lines[1:]:
            word, effort = line.split("\t")
            if word in word_set:
                scores.append(float(effort))
    return sorted(scores)


def parse_tidy_attributes(stderr: str) -> dict:
    """Parse tidy's attribute output into a dict."""
    attrs = {}
    for line in stderr.splitlines():
        match = re.match(r"\s*(.+?)\s+:\s+(.+)", line)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            attrs[key] = value
    return attrs


def compute_stats(word_list: list[str], input_count: int, tidy_attrs: dict) -> dict:
    """Compute all stats for the word list."""
    count = len(word_list)
    entropy = math.log2(count) if count > 0 else 0
    lengths = [len(w) for w in word_list]
    mean_len = statistics.mean(lengths) if lengths else 0
    efficiency = entropy / mean_len if mean_len > 0 else 0

    # Typing effort scores
    word_set = set(word_list)
    scores = load_typing_scores(word_set)
    n = len(scores)

    # Passphrase estimates
    passphrases = {}
    for num_words in [4, 5, 6, 7, 8, 10]:
        bits = num_words * entropy
        chars = num_words * mean_len + (num_words - 1)
        passphrases[str(num_words)] = {
            "entropy_bits": round(bits, 1),
            "length_chars": round(chars, 0),
        }

    return {
        "list": {
            "words": count,
            "input_words": input_count,
            "removed_by_tidy": input_count - count,
            "entropy_per_word": round(entropy, 3),
            "mean_word_length": round(mean_len, 2),
            "efficiency_per_char": round(efficiency, 3),
            "shortest_word": min(lengths),
            "longest_word": max(lengths),
        },
        "tidy_attributes": {
            "free_of_prefix_words": tidy_attrs.get("Free of prefix words?", ""),
            "free_of_suffix_words": tidy_attrs.get("Free of suffix words?", ""),
            "uniquely_decodable": tidy_attrs.get("Uniquely decodable?", ""),
            "above_brute_force_line": tidy_attrs.get("Above brute force line?", ""),
            "shortest_edit_distance": tidy_attrs.get("Shortest edit distance", ""),
            "mean_edit_distance": tidy_attrs.get("Mean edit distance", ""),
            "unique_character_prefix": tidy_attrs.get("Unique character prefix", ""),
            "kraft_mcmillan": tidy_attrs.get("Kraft-McMillan inequality", ""),
        },
        "typing_effort": {
            "words_with_scores": n,
            "minimum": round(scores[0], 2) if scores else None,
            "percentile_10": round(scores[n // 10], 2) if scores else None,
            "percentile_25": round(scores[n // 4], 2) if scores else None,
            "median": round(statistics.median(scores), 2) if scores else None,
            "mean": round(statistics.mean(scores), 2) if scores else None,
            "percentile_75": round(scores[3 * n // 4], 2) if scores else None,
            "percentile_90": round(scores[9 * n // 10], 2) if scores else None,
            "maximum": round(scores[-1], 2) if scores else None,
            "pct_below_1_8": round(sum(1 for s in scores if s < 1.8) / n * 100) if n else None,
            "pct_below_2_0": round(sum(1 for s in scores if s < 2.0) / n * 100) if n else None,
        },
        "passphrases": passphrases,
    }


def write_stats(stats: dict) -> None:
    """Write stats to docs/stats.json."""
    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATS_PATH.write_text(json.dumps(stats, indent=2) + "\n")


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
        "-P",  # Remove remaining prefix words
        "-S",  # Remove remaining suffix words
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
    print("\nRunning tidy (Schlinkert pruning + prefix/suffix removal)...")
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

    # Parse tidy attributes and compute full stats
    tidy_attrs = parse_tidy_attributes(result.stderr)
    word_list = out_path.read_text().strip().splitlines()
    stats = compute_stats(word_list, len(all_words), tidy_attrs)
    write_stats(stats)

    # Print summary
    s = stats["list"]
    print(f"\nFinal word list: {out_path}")
    print(f"  Words: {s['words']}")
    print(f"  Entropy per word: {s['entropy_per_word']} bits")
    print(f"  Mean word length: {s['mean_word_length']} characters")
    print(f"  Input words: {s['input_words']}")
    print(f"  Removed by tidy: {s['removed_by_tidy']}")
    print(f"  Stats written to: {STATS_PATH}")


if __name__ == "__main__":
    main()
