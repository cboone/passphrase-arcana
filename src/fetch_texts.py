"""Step 1: Download texts from Standard Ebooks (preferred) and Project Gutenberg.

Standard Ebooks texts are professionally proofread and have cleaner
formatting than Gutenberg. When a work is available on SE, it is
preferred. Gutenberg is used as a fallback for works not on SE.
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

from gutenberg import fetch_text
from standardebooks import fetch_se_text

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
        se_sources = lang_cfg.get("standard_ebooks", {})

        # Build set of authors that have SE sources
        # For these authors, fetch SE texts first, then fill in with Gutenberg
        for author, ebook_ids in sources.items():
            se_slugs = se_sources.get(author, [])

            # Fetch Standard Ebooks texts (preferred)
            for slug in se_slugs:
                total += 1
                # Use slug's book part as filename
                book_name = slug.split("/")[-1]
                dest = DATA_RAW / lang / f"{author}_se_{book_name}.txt"
                try:
                    was_new = fetch_se_text(slug, dest)
                    if was_new:
                        downloaded += 1
                        print(f"  [{lang_name}] {author} SE:{book_name} -> {dest.name}")
                    else:
                        print(f"  [{lang_name}] {author} SE:{book_name} (cached)")
                except Exception as exc:
                    errors += 1
                    print(
                        f"  [{lang_name}] {author} SE:{book_name} ERROR: {exc}",
                        file=sys.stderr,
                    )

            # Fetch Gutenberg texts (fallback / additional works)
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
                    print(
                        f"  [{lang_name}] {author} #{ebook_id} ERROR: {exc}",
                        file=sys.stderr,
                    )

        # Handle authors that only have SE sources (no Gutenberg IDs)
        for author, se_slugs in se_sources.items():
            if author in sources:
                continue  # Already handled above
            for slug in se_slugs:
                total += 1
                book_name = slug.split("/")[-1]
                dest = DATA_RAW / lang / f"{author}_se_{book_name}.txt"
                try:
                    was_new = fetch_se_text(slug, dest)
                    if was_new:
                        downloaded += 1
                        print(f"  [{lang_name}] {author} SE:{book_name} -> {dest.name}")
                    else:
                        print(f"  [{lang_name}] {author} SE:{book_name} (cached)")
                except Exception as exc:
                    errors += 1
                    print(
                        f"  [{lang_name}] {author} SE:{book_name} ERROR: {exc}",
                        file=sys.stderr,
                    )

    print(f"\nDone: {downloaded} downloaded, {total - downloaded - errors} cached, {errors} errors")


if __name__ == "__main__":
    main()
