"""Tests for scripts/onomasticon_match.py, including the boilerplate-filter
fix for the Gutenberg-artifact noise ("com", "project") that was previously
inflating the BoM/Lahontan "shared proper noun" count.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import onomasticon_match


def test_get_proper_nouns_excludes_gutenberg_boilerplate():
    text = ("This is a Project Gutenberg eBook. Visit www.gutenberg.org or "
            "email a Project volunteer for information about Project rules.")
    nouns = onomasticon_match.get_proper_nouns(text)
    assert "project" not in nouns
    assert "gutenberg" not in nouns


def test_get_proper_nouns_keeps_real_mid_sentence_names():
    # Mid-sentence detection is checked within a single sentence at a time,
    # so the name must follow a lowercase word directly (no intervening
    # punctuation) at least once in that sentence to register.
    text = "We went to see Nephi and Zarahemla today, since Nephi lives near Zarahemla."
    nouns = onomasticon_match.get_proper_nouns(text)
    assert "nephi" in nouns
    assert "zarahemla" in nouns


def test_get_proper_nouns_drops_sentence_initial_only_capitals():
    text = "The dog ran. The cat sat. The bird flew."
    nouns = onomasticon_match.get_proper_nouns(text)
    assert "the" not in nouns


def test_match_returns_intersection_and_counts():
    a = "We saw Nephi meet Lehi. They called Nephi and Lehi great leaders."
    b = "Ships carried Lehi. Records mention Lehi and also Nephi, who led them."
    result = onomasticon_match.match(a, b)
    assert result["match_count"] == len(result["matches"])
    assert "lehi" in result["matches"]
