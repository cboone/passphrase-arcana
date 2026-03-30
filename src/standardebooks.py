"""Helpers for fetching and cleaning Standard Ebooks texts.

Standard Ebooks provides professionally proofread public domain texts
in clean XHTML. We fetch the single-page HTML view and strip tags to
get plain text, which is cleaner than the Gutenberg versions (no
header/footer boilerplate, consistent formatting).
"""

from __future__ import annotations

import re
import time
from html.parser import HTMLParser
from pathlib import Path

import httpx

SE_TEXT_URL = "https://standardebooks.org/ebooks/{slug}/text/single-page"


class _TextExtractor(HTMLParser):
    """Extract visible text from Standard Ebooks HTML, skipping boilerplate."""

    # Sections to skip: front matter, back matter, colophon, etc.
    _SKIP_TYPES = {"titlepage", "imprint", "colophon", "copyright-page", "toc", "loi"}

    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0
        self._in_skip = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_dict = dict(attrs)
        epub_type = attr_dict.get("epub:type", "")
        # Skip boilerplate sections
        if any(st in epub_type for st in self._SKIP_TYPES):
            self._in_skip = True
            self._skip_depth = 1
        elif self._in_skip:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._in_skip:
            self._skip_depth -= 1
            if self._skip_depth <= 0:
                self._in_skip = False

    def handle_data(self, data: str) -> None:
        if not self._in_skip:
            self.parts.append(data)

    def get_text(self) -> str:
        return " ".join(self.parts)


def fetch_se_text(slug: str, dest: Path, delay: float = 1.0) -> bool:
    """Download a Standard Ebooks text to dest.

    Returns True if downloaded, False if already cached.
    The slug is the SE URL path, e.g. "herman-melville/moby-dick".
    """
    if dest.exists() and dest.stat().st_size > 0:
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)
    url = SE_TEXT_URL.format(slug=slug)

    with httpx.Client(follow_redirects=True, timeout=30.0) as client:
        resp = client.get(url)
        resp.raise_for_status()

    # Extract text from HTML
    extractor = _TextExtractor()
    extractor.feed(resp.text)
    text = extractor.get_text()

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Re-add paragraph breaks for readability
    text = re.sub(r"\s*\n\s*", "\n", text)

    dest.write_text(text, encoding="utf-8")
    time.sleep(delay)
    return True
