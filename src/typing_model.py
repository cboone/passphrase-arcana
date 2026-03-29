"""QWERTY typing effort model inspired by Carpalx and the Typability Index.

Scores individual words by combining per-key base effort (finger strength,
row distance) with bigram transition effort (same-finger penalties, roll
direction, hand alternation). The result is normalized per character so
word length does not bias the score.
"""

from __future__ import annotations

# Finger assignments: L=left, R=right; P=pinky, R=ring, M=middle, I=index
FINGER_MAP: dict[str, str] = {
    "q": "LP",
    "w": "LR",
    "e": "LM",
    "r": "LI",
    "t": "LI",
    "y": "RI",
    "u": "RI",
    "i": "RM",
    "o": "RR",
    "p": "RP",
    "a": "LP",
    "s": "LR",
    "d": "LM",
    "f": "LI",
    "g": "LI",
    "h": "RI",
    "j": "RI",
    "k": "RM",
    "l": "RR",
    "z": "LP",
    "x": "LR",
    "c": "LM",
    "v": "LI",
    "b": "LI",
    "n": "RI",
    "m": "RI",
}

# Row: 0 = home, 1 = top, -1 = bottom
ROW_MAP: dict[str, int] = {
    "q": 1,
    "w": 1,
    "e": 1,
    "r": 1,
    "t": 1,
    "y": 1,
    "u": 1,
    "i": 1,
    "o": 1,
    "p": 1,
    "a": 0,
    "s": 0,
    "d": 0,
    "f": 0,
    "g": 0,
    "h": 0,
    "j": 0,
    "k": 0,
    "l": 0,
    "z": -1,
    "x": -1,
    "c": -1,
    "v": -1,
    "b": -1,
    "n": -1,
    "m": -1,
}

# Per-key base effort combining row distance and finger strength.
# Finger strength factors: index=1.0, middle=1.1, ring=1.3, pinky=1.6
# Row penalties: home=0, top=+0.5, bottom=+0.8
# Center column lateral stretch: +0.3
KEY_EFFORT: dict[str, float] = {
    # Home row
    "a": 1.6,
    "s": 1.3,
    "d": 1.1,
    "f": 1.0,
    "g": 1.3,
    "h": 1.3,
    "j": 1.0,
    "k": 1.1,
    "l": 1.3,
    # Top row
    "q": 2.4,
    "w": 1.95,
    "e": 1.65,
    "r": 1.5,
    "t": 1.8,
    "y": 1.8,
    "u": 1.5,
    "i": 1.65,
    "o": 1.95,
    "p": 2.4,
    # Bottom row
    "z": 2.88,
    "x": 2.34,
    "c": 1.98,
    "v": 1.8,
    "b": 2.1,
    "n": 1.8,
    "m": 1.8,
}

_FINGER_ORDER = {"I": 0, "M": 1, "R": 2, "P": 3}


def bigram_effort(c1: str, c2: str) -> float:
    """Calculate transition effort between two consecutive characters."""
    if c1 not in FINGER_MAP or c2 not in FINGER_MAP:
        return 0.0

    f1, f2 = FINGER_MAP[c1], FINGER_MAP[c2]
    hand1, hand2 = f1[0], f2[0]
    finger1, finger2 = f1[1], f2[1]
    row1, row2 = ROW_MAP[c1], ROW_MAP[c2]

    effort = 0.0

    if hand1 == hand2:
        if finger1 == finger2:
            # Same finger: worst case
            row_distance = abs(row1 - row2)
            if row_distance == 0:
                effort += 2.5  # Same key repeated
            else:
                effort += 2.5 + row_distance * 1.5
        else:
            # Same hand, different finger: check roll direction
            direction = _FINGER_ORDER[finger2] - _FINGER_ORDER[finger1]
            if hand1 == "L":
                # Left hand: inward roll = increasing finger order (index toward pinky)
                effort += -0.5 if direction > 0 else 0.5
            else:
                # Right hand: inward roll = decreasing finger order
                effort += -0.5 if direction < 0 else 0.5
            # Row change penalty on same hand
            effort += abs(row1 - row2) * 0.3
    else:
        # Hand alternation bonus
        effort += -0.3

    return max(effort, 0.0)


def word_effort(word: str) -> float:
    """Calculate typing effort for a word, normalized per character.

    Returns float('inf') for words containing characters not on the QWERTY
    letter keys (a-z).
    """
    if not word:
        return float("inf")
    if not all(c in KEY_EFFORT for c in word):
        return float("inf")

    base = sum(KEY_EFFORT[c] for c in word)
    transitions = sum(bigram_effort(word[i], word[i + 1]) for i in range(len(word) - 1))
    return (base + transitions) / len(word)
