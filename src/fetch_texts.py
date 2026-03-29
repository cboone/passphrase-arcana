"""Step 1: Download Project Gutenberg texts listed in config.toml."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from gutenberg import fetch_text

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config.toml"
DATA_RAW = ROOT / "data" / "raw"


def main() -> None:
    config = tomllib.loads(CONFIG.read_text())
    languages = config["languages"]

    total = 0
    downloaded = 0
    errors = 0

    for lang, lang_cfg in languages.items():
        lang_name = lang_cfg["name"]
        sources = lang_cfg.get("sources", {})
        for author, ebook_ids in sources.items():
            for ebook_id in ebook_ids:
                total += 1
                dest = DATA_RAW / lang / f"{author}_{ebook_id}.txt"
                try:
                    was_new = fetch_text(ebook_id, dest)
                    if was_new:
                        downloaded += 1
                        print(f"  [{lang_name}] {author} #{ebook_id} -> {dest.name}")
                    else:
                        print(f"  [{lang_name}] {author} #{ebook_id} (cached)")
                except Exception as exc:
                    errors += 1
                    print(f"  [{lang_name}] {author} #{ebook_id} ERROR: {exc}", file=sys.stderr)

    print(f"\nDone: {downloaded} downloaded, {total - downloaded - errors} cached, {errors} errors")


if __name__ == "__main__":
    main()
