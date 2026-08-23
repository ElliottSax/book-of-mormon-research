"""Tests for the word-level n-gram text-reuse detector in scripts/textreuse.py.

Includes a regression check that a common short phrase doesn't spuriously
dominate results the way it would under the old character-shingle approach.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import textreuse

SHARED_PHRASE = "the curious workmanship of the compass"

TEXT_A = f"Long ago in a distant land, {SHARED_PHRASE} amazed everyone who saw it work."
TEXT_B = f"In another story entirely, {SHARED_PHRASE} was described in exact detail."
UNRELATED = "Quarterly rainfall in the region varied considerably across the decade studied."


def test_shared_phrase_scores_high_overlap():
    overlaps = textreuse.top_overlaps(TEXT_A, TEXT_B, n=6, top_k=5)
    assert overlaps, "expected at least one overlapping 6-gram"
    top_gram, top_score = overlaps[0]
    assert "curious workmanship" in top_gram
    assert top_score > 0.05


def test_unrelated_texts_score_near_zero():
    overlaps = textreuse.top_overlaps(TEXT_A, UNRELATED, n=6, top_k=5)
    assert overlaps == []


def test_common_short_substring_does_not_dominate():
    # Under the old char-5-gram approach, a common substring like " the "
    # would show up as a top "overlap" between almost any two English texts.
    # Word-level n-grams (n=6) require a genuinely shared phrase, not just a
    # shared function word, so two texts sharing only "the" should not
    # register any overlap at n=6.
    a = "the cat sat on the old wooden mat by the door"
    b = "the dog ran across the wide green field near the river"
    overlaps = textreuse.top_overlaps(a, b, n=6, top_k=5)
    assert overlaps == []


def test_jaccard_similarity_reflects_shared_vocabulary():
    grams_a = textreuse.word_ngrams(TEXT_A, n=6)
    grams_b = textreuse.word_ngrams(TEXT_B, n=6)
    sim_related = textreuse.jaccard_similarity(grams_a, grams_b)
    grams_unrelated = textreuse.word_ngrams(UNRELATED, n=6)
    sim_unrelated = textreuse.jaccard_similarity(grams_a, grams_unrelated)
    assert sim_related > sim_unrelated
