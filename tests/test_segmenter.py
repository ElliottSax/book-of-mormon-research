"""Tests for segmenter.py against the real Book of Mormon corpus text.

Includes a direct regression test for the bug this module was written to
fix: the previous heading-detection heuristic misattributed the sole
"Liahona" occurrence to a `None`/`null` book bucket instead of Alma 37.
"""
from pathlib import Path

import pytest

import corpus
import segmenter

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def bom_raw():
    return corpus.load_text(corpus.BOM_PATH)


@pytest.fixture(scope="module")
def index(bom_raw):
    return segmenter.build_index(bom_raw)


def test_finds_all_15_canonical_books(index):
    assert len(index) == 15
    assert [b for b, _ in segmenter.BOM_BOOKS] == list(index.keys())


def test_total_verse_count_in_expected_range(index):
    total = sum(len(chapters) for book in index.values() for chapters in book.values())
    lo, hi = segmenter.EXPECTED_VERSE_COUNT_RANGE
    assert lo <= total <= hi


def test_liahona_lands_in_alma_37_not_null(index):
    """Regression test for the found bug: reports/liahona_segment.json
    previously showed {"null": 1} instead of attributing the hit to Alma.
    """
    dist = segmenter.term_distribution(index, "Liahona")
    assert dist["total"] == 1
    assert "Alma" in dist["by_book"]
    assert dist["by_book"]["Alma"]["by_chapter"] == {37: 1}


def test_ball_cluster_in_1_nephi_16(index):
    # "ball" is the term that actually clusters in 1 Nephi 16 (where the
    # Liahona is introduced/described); "compass" itself is used later,
    # when the family is at sea (1 Nephi 18) and in the Alma 37 gloss.
    dist = segmenter.term_distribution(index, "ball")
    assert "1 Nephi" in dist["by_book"]
    assert dist["by_book"]["1 Nephi"]["by_chapter"].get(16, 0) >= 5


def test_parse_contents_matches_bom_books_order(bom_raw):
    headings = segmenter.parse_contents(bom_raw)
    expected = [h for _, h in segmenter.BOM_BOOKS]
    assert headings == expected
