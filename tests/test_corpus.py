"""Tests for corpus.py's integrity verification.

Regression coverage for the exact corruption class found during the repo
audit: texts/aeneid.txt and texts/aeneid_dryden.txt were saved HTTP
error/failure pages, not real text, and silently passed through the old
loader with no check.
"""
import pytest

import corpus


def test_verify_text_integrity_accepts_plausible_text():
    text = " ".join(["word"] * 2000)
    corpus.verify_text_integrity("fixture", text)  # should not raise


def test_verify_text_integrity_rejects_archive_org_error_page():
    text = '<!DOCTYPE html><html><head><title>Internet Archive: Error</title></head></html>'
    with pytest.raises(corpus.CorruptTextError):
        corpus.verify_text_integrity("fixture", text)


def test_verify_text_integrity_rejects_gateway_timeout_page():
    text = "<html><body><h1>504 Gateway Time-out</h1>The server didn't respond in time.</body></html>"
    with pytest.raises(corpus.CorruptTextError):
        corpus.verify_text_integrity("fixture", text)


def test_verify_text_integrity_rejects_too_short_text():
    with pytest.raises(corpus.CorruptTextError):
        corpus.verify_text_integrity("fixture", "just a few words here")


def test_get_all_texts_loads_all_four_and_passes_integrity(tmp_path=None):
    texts = corpus.get_all_texts()
    assert set(texts.keys()) == {"book_of_mormon", "spalding_manuscript", "lahontan_new_voyages", "aeneid"}
    for name, text in texts.items():
        assert len(text.split()) > corpus.MIN_PLAUSIBLE_WORDS, name


def test_detect_liahona_spelling_finds_liahona():
    matches = corpus.detect_liahona_spelling("...called it Liahona, which is...")
    assert matches == ["Liahona"]
