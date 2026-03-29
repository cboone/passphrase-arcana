"""Helpers for fetching and cleaning Project Gutenberg texts."""

from __future__ import annotations

import re
import time
from pathlib import Path

import httpx

GUTENBERG_URL = "https://www.gutenberg.org/cache/epub/{ebook_id}/pg{ebook_id}.txt"

# Patterns to find the start/end of the actual text content
START_MARKERS = [
    re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG", re.IGNORECASE),
    re.compile(r"\*\*\*\s*START OF THE PROJECT", re.IGNORECASE),
]
END_MARKERS = [
    re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG", re.IGNORECASE),
    re.compile(r"\*\*\*\s*END OF THE PROJECT", re.IGNORECASE),
]


def fetch_text(ebook_id: int, dest: Path, delay: float = 1.0) -> bool:
    """Download a Gutenberg text to dest. Returns True if downloaded, False if already exists."""
    if dest.exists() and dest.stat().st_size > 0:
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    url = GUTENBERG_URL.format(ebook_id=ebook_id)

    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        resp = client.get(url)
        resp.raise_for_status()

    raw = resp.text
    cleaned = strip_gutenberg_boilerplate(raw)
    dest.write_text(cleaned, encoding="utf-8")
    time.sleep(delay)
    return True


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove Project Gutenberg header and footer from a text."""
    lines = text.splitlines()

    start_idx = 0
    for i, line in enumerate(lines):
        if any(m.search(line) for m in START_MARKERS):
            start_idx = i + 1
            break

    end_idx = len(lines)
    for i in range(len(lines) - 1, start_idx, -1):
        if any(m.search(lines[i]) for m in END_MARKERS):
            end_idx = i
            break

    return "\n".join(lines[start_idx:end_idx])
