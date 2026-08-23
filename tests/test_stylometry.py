"""Sanity tests for the stylometry pipeline using synthetic controls.

Control 1: same-source split — half of one text vs. the other half of the
same text should show high cosine similarity (it is the same author).
Control 2: different-source — King James Bible text vs. a random sentence
should show low similarity, and distinctive words should highlight the
divergence.
"""
import random
from stylometry import word_counts, profile, cosine_similarity, compare_texts, tokenize, markered_density, liahona_term_counts

SAMPLE_A = " ".join(["the quick brown fox jumps over the lazy dog"] * 40)
SAMPLE_B = " ".join(["now is the winter of our discontent made glorious summer"] * 40)

def test_tokenize():
    toks = tokenize("Hello, world! Hello world again.")
    assert toks == ["hello", "world", "hello", "world", "again"]

def test_same_source_high_similarity():
    half = len(SAMPLE_A.split()) // 2
    a = " ".join(SAMPLE_A.split()[:half])
    b = " ".join(SAMPLE_A.split()[half:])
    sim = cosine_similarity(word_counts(a), word_counts(b))
    assert sim > 0.9, f"expected high self-similarity, got {sim}"

def test_different_sources_low_similarity():
    sim = cosine_similarity(word_counts(SAMPLE_A), word_counts(SAMPLE_B))
    assert sim < 0.8, f"expected lower cross-similarity, got {sim}"

def test_profile_metrics_basic():
    p = profile(SAMPLE_A)
    assert p["total_words"] == 360
    assert p["unique_words"] == 8
    assert abs(p["ttr"] - 8/360) < 1e-6

def test_distinctive_words_flag_marker():
    res = compare_texts("a", SAMPLE_A, "b", SAMPLE_B)
    words_a = [d["word"] for d in res["distinctive_a_over_b"][:3]]
    assert "brown" in words_a, f"expected 'brown' distinctive of A, got {words_a}"

BOM_SPICE = ("And it came to pass that behold, the Lord said unto Nephi, "
             "yea, and verily thou art blessed with the compass and the director, "
             "and the ball of curious workmanship which is the Liahona.")

def test_emodern_phrase_counts_detect_spanning_markers():
    # Regression: multi-word phrases ("and it came to pass") must register,
    # not silently vanish because they are not single tokens.
    md = markered_density(BOM_SPICE)
    assert md["phrase_hits"] >= 2, f"expected >=1 'and it came to pass' hit, got {md}"
    assert md["single_hits"] >= 4, f"expected behold/yea/verily/thou hits, got {md}"
    assert md["density"] > 0

def test_liahona_terms_detect_compass_vocab():
    counts = liahona_term_counts(BOM_SPICE)
    for t in ("liahona", "compass", "director", "ball"):
        assert counts[t] >= 1, f"term '{t}' not detected: {counts}"

def test_profile_includes_emodern_and_liahona():
    p = profile(BOM_SPICE)
    assert p["emodern_density"] == markered_density(BOM_SPICE)["density"]
    assert p["liahona_terms"]["liahona"] >= 1

if __name__ == "__main__":
    import sys
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    sys.exit(1 if failed else 0)
