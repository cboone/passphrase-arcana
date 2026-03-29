"""Tests for the proper noun filter."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from filter_proper_nouns import filter_proper_nouns, scan_lowercase_tokens


class TestScanLowercaseTokens:
    def test_finds_lowercase_words(self, tmp_path):
        (tmp_path / "text.txt").write_text("The whale swam deep. Ahab watched.")
        result = scan_lowercase_tokens(tmp_path, 3, 9)
        assert "whale" in result
        assert "swam" in result
        assert "deep" in result
        assert "watched" in result

    def test_excludes_always_capitalized(self, tmp_path):
        (tmp_path / "text.txt").write_text("Ahab spoke. Ahab watched. Ahab left.")
        result = scan_lowercase_tokens(tmp_path, 3, 9)
        assert "ahab" not in result

    def test_respects_length_bounds(self, tmp_path):
        (tmp_path / "text.txt").write_text("a be cat dogs elephants")
        result = scan_lowercase_tokens(tmp_path, 4, 9)
        assert "a" not in result
        assert "be" not in result
        assert "cat" not in result
        assert "dogs" in result
        assert "elephants" in result

    def test_handles_multiple_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("Ishmael sailed the seas.")
        (tmp_path / "b.txt").write_text("Call me ishmael, he said.")
        result = scan_lowercase_tokens(tmp_path, 4, 9)
        # "ishmael" appears lowercase in b.txt
        assert "ishmael" in result
        assert "sailed" in result

    def test_handles_empty_directory(self, tmp_path):
        result = scan_lowercase_tokens(tmp_path, 4, 9)
        assert result == set()

    def test_concordance_style_all_lowercase(self, tmp_path):
        (tmp_path / "concordance.txt").write_text("danaher\nmclendon\nfatalism\n")
        result = scan_lowercase_tokens(tmp_path, 4, 9)
        assert "danaher" in result
        assert "mclendon" in result
        assert "fatalism" in result


def _write_csv(path, rows):
    """Helper to write a word_frequencies.csv file."""
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["word", "count", "num_authors", "original_forms"])
        writer.writeheader()
        writer.writerows(rows)


class TestFilterProperNouns:
    def test_removes_proper_nouns(self, tmp_path):
        csv_path = tmp_path / "word_frequencies.csv"
        _write_csv(
            csv_path,
            [
                {"word": "ahab", "count": "50", "num_authors": "1", "original_forms": "ahab"},
                {"word": "whale", "count": "200", "num_authors": "5", "original_forms": "whale"},
                {
                    "word": "starbuck",
                    "count": "30",
                    "num_authors": "1",
                    "original_forms": "starbuck",
                },
            ],
        )
        seen = {"whale", "darkness"}
        kept, removed = filter_proper_nouns(csv_path, seen)
        assert len(kept) == 1
        assert kept[0]["word"] == "whale"
        assert sorted(removed) == ["ahab", "starbuck"]

    def test_keeps_all_when_all_seen(self, tmp_path):
        csv_path = tmp_path / "word_frequencies.csv"
        _write_csv(
            csv_path,
            [
                {"word": "dark", "count": "10", "num_authors": "3", "original_forms": "dark"},
                {"word": "whale", "count": "20", "num_authors": "5", "original_forms": "whale"},
            ],
        )
        seen = {"dark", "whale"}
        kept, removed = filter_proper_nouns(csv_path, seen)
        assert len(kept) == 2
        assert removed == []

    def test_handles_empty_csv(self, tmp_path):
        csv_path = tmp_path / "word_frequencies.csv"
        _write_csv(csv_path, [])
        kept, removed = filter_proper_nouns(csv_path, {"whale"})
        assert kept == []
        assert removed == []
