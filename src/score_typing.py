"""Step 4: Score validated words for typing difficulty and filter."""

from __future__ import annotations

import tomllib
from pathlib import Path

from typing_model import word_effort

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_VALIDATED = ROOT / "data" / "validated"
DATA_SCORED = ROOT / "data" / "scored"


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    max_effort = config["typing"]["max_effort_per_char"]
    languages = config["languages"]

    DATA_SCORED.mkdir(parents=True, exist_ok=True)

    for lang, lang_cfg in languages.items():
        lang_name = lang_cfg["name"]
        validated_path = DATA_VALIDATED / f"{lang}_validated.txt"

        if not validated_path.exists():
            print(f"[{lang_name}] No validated words found, skipping")
            continue

        words = validated_path.read_text().strip().splitlines()
        scored = []
        filtered_out = 0

        for word in words:
            effort = word_effort(word)
            if effort <= max_effort:
                scored.append((word, effort))
            else:
                filtered_out += 1

        scored.sort(key=lambda x: x[0])

        out_path = DATA_SCORED / f"{lang}_scored.tsv"
        lines = ["word\teffort"]
        for word, effort in scored:
            lines.append(f"{word}\t{effort:.4f}")
        out_path.write_text("\n".join(lines) + "\n")

        efforts = [e for _, e in scored]
        mean_effort = sum(efforts) / len(efforts) if efforts else 0
        print(
            f"[{lang_name}] {len(scored)} words pass typing filter "
            f"({filtered_out} removed, mean effort {mean_effort:.3f})"
        )


if __name__ == "__main__":
    main()
