"""Tests for the QWERTY typing effort model."""

from __future__ import annotations

import sys
from pathlib import Path

# Add src to path so we can import the module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from typing_model import KEY_EFFORT, bigram_effort, word_effort


class TestKeyEffort:
    def test_home_row_keys_exist(self):
        for key in "asdfghjkl":
            assert key in KEY_EFFORT

    def test_all_letters_covered(self):
        for c in "abcdefghijklmnopqrstuvwxyz":
            assert c in KEY_EFFORT, f"Missing key: {c}"

    def test_home_row_cheaper_than_others(self):
        home_avg = sum(KEY_EFFORT[c] for c in "asdfghjkl") / 9
        top_avg = sum(KEY_EFFORT[c] for c in "qwertyuiop") / 10
        bottom_avg = sum(KEY_EFFORT[c] for c in "zxcvbnm") / 7
        assert home_avg < top_avg
        assert home_avg < bottom_avg

    def test_index_finger_cheaper_than_pinky(self):
        assert KEY_EFFORT["f"] < KEY_EFFORT["a"]  # Left hand home row
        assert KEY_EFFORT["j"] < KEY_EFFORT["l"]  # Right hand home row (l is ring, not pinky, but close)


class TestBigramEffort:
    def test_hand_alternation_is_cheap(self):
        # f (left index) -> j (right index) should be very cheap (hand alternation)
        assert bigram_effort("f", "j") == 0.0  # -0.3 floored to 0

    def test_same_finger_is_expensive(self):
        # e -> d: same finger (left middle), different row
        effort = bigram_effort("e", "d")
        assert effort > 2.0

    def test_same_key_repeated(self):
        effort = bigram_effort("s", "s")
        assert effort >= 2.5

    def test_inward_roll_cheaper_than_outward(self):
        # Left hand: f->d (index to middle = inward) vs d->f (middle to index = outward)
        inward = bigram_effort("f", "d")   # index -> middle on left = inward roll
        outward = bigram_effort("d", "f")  # middle -> index on left = outward roll
        assert inward < outward

    def test_unknown_char_returns_zero(self):
        assert bigram_effort("a", "1") == 0.0
        assert bigram_effort("!", "a") == 0.0


class TestWordEffort:
    def test_empty_string(self):
        assert word_effort("") == float("inf")

    def test_non_alpha_returns_inf(self):
        assert word_effort("hello1") == float("inf")
        assert word_effort("test!") == float("inf")

    def test_home_row_word_is_cheap(self):
        # "flash" uses mostly home row and easy keys
        effort = word_effort("flash")
        assert effort < 2.0

    def test_awkward_word_is_expensive(self):
        # "zxcv" uses bottom row pinky/ring/middle/index
        effort = word_effort("zxcv")
        assert effort > 2.0

    def test_normalized_by_length(self):
        # Effort should be per-character, so similar words of different length
        # should have similar scores if they use similar keys
        short = word_effort("the")
        long = word_effort("thethe")
        # Should be in the same ballpark (not exactly equal due to bigrams)
        assert abs(short - long) < 1.0

    def test_easy_words_score_low(self):
        for word in ["hand", "fish", "silk", "then", "lake"]:
            assert word_effort(word) < 2.0, f"{word} should be easy to type"

    def test_hard_words_score_high(self):
        for word in ["puppy", "plumb", "jazzy"]:
            assert word_effort(word) > 2.5, f"{word} should be hard to type"
