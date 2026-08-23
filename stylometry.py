"""Stylometric comparison pipeline for Book of Mormon authorship research.

Computes:
  - lexical frequency profiles (word-level)
  - distinctive-word overlap between texts
  - cosine similarity between frequency vectors
  - per-text statistics: type/token ratio, hapax legomena, average word length
  - paired "voice" analysis (relative usage of function words, pronouns, etc.)
"""
from __future__ import annotations

import re
from collections import Counter

# Common English function words / pronouns that are strong stylometric markers.
FUNCTION_WORDS = {
    "the", "and", "of", "to", "a", "in", "that", "it", "was", "for", "is",
    "with", "as", "on", "by", "be", "this", "which", "or", "but", "not",
    "from", "were", "been", "had", "have", "their", "there", "an", "would",
    "when", "all", "these", "those", "they", "he", "she", "his", "her",
    "them", "him", "my", "your", "our", "we", "you", "i", "us", "than",
    "then", "so", "because", "therefore", "behold",
}

# Early Modern English / KJV-flavored markers heavily overrepresented in the
# Book of Mormon's translation dialect. Comparing their density across texts
# is a fast, decisive voice check for the Spalding / Lahontan theories.
# Single tokens are matched against a word counter; multi-word phrases are
# matched against the lowercased raw text so they register correctly.
EMODERN_SINGLE = {"behold", "ye", "thou", "thee", "thy", "thine", "hath", "doth",
                  "wherefore", "verily", "whoso", "unto", "ought", "yea", "nay",
                  "cometh", "goeth", "saith", "dwelleth", "casteth", "beholdeth"}
EMODERN_PHRASES = {"and it came to pass", "it came to pass", "even so", "and so it was"}

# 1 Nephi 16's Liahona vocabulary — the specific Lahontan-connection probe.
LIAHONA_TERMS = {"liahona", "director", "compass", "ball", "pointers"}

# Vocabulary for the conceptual (not just lexical) Lahontan-connection probe:
# Lahontan's New Voyages, Vol. II describes indigenous peoples attributing
# spiritual agency to a "Compafs" [Compass] and other instruments ("moved by
# Spirits", "took my Graphometer for somewhat Divine... some Supernatural
# Assistance") -- thematically adjacent to the Liahona's faith-dependent
# operation (Alma 37:40), though framed very differently (a skeptical
# European's mocking anecdote about "ignorant" natives, vs. the Book of
# Mormon's own reverent first-person framing). See RESEARCH_LOG.md.
SPIRIT_INSTRUMENT_TERMS = {"spirit", "spirits", "divine", "supernatural", "machine", "machines", "faith"}

def ocr_tolerant_pattern(word: str) -> str:
    """Build a regex pattern for `word` that also matches the historical
    "long s" OCR misread common in 18th/19th-century scanned texts: a
    non-word-final lowercase 's' was typeset as a long-s glyph, which OCR
    frequently reads as 'f' (e.g. Lahontan's "compass" scans as "compafs" or
    "compaff"). Word-final 's' is left literal, since the long-s form was
    never used there. Found necessary in practice: a literal-string search
    for "compass" in the Lahontan corpus returned zero hits even though the
    word appears 7 times, purely because of this OCR artifact.
    """
    chars = list(word)
    n = len(chars)
    for i, c in enumerate(chars):
        if c.lower() == "s" and i != n - 1:
            chars[i] = "[sf]"
        else:
            chars[i] = re.escape(c)
    return "".join(chars)

def tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())

def word_counts(text: str) -> Counter:
    return Counter(tokenize(text))

def markered_density(text: str) -> dict:
    """Count single-token EMODERN markers and multi-word phrases in raw text."""
    lower = text.lower()
    singles = Counter(tokenize(text))
    single_hits = sum(singles[w] for w in EMODERN_SINGLE)
    phrase_hits = sum(lower.count(p) for p in EMODERN_PHRASES)
    total = len(tokenize(text))
    return {"single_hits": single_hits, "phrase_hits": phrase_hits,
            "total": total, "density": (single_hits + phrase_hits) / total if total else 0.0}

_LIAHONA_TERM_PATTERNS = {
    t: re.compile(rf"\b{ocr_tolerant_pattern(t)}\b", re.IGNORECASE) for t in LIAHONA_TERMS
}

def liahona_term_counts(text: str) -> dict:
    """Whole-word usage counts of Lahontan-connected Liahona vocabulary.

    Uses word-boundary, OCR-long-s-tolerant matching, not raw substring
    counting: a prior version counted "compass" via `text.count("compass")`,
    which silently included "compassed" and "compassion" -- unrelated words
    -- inflating the BoM compass count from 7 (the real navigational-device
    references) to 22. A separate prior version switched to a literal
    word-boundary regex but that undercounted "compass" to 0 in the Lahontan
    corpus, because that text's OCR renders it "compafs"/"compaff".
    """
    return {t: len(pattern.findall(text)) for t, pattern in _LIAHONA_TERM_PATTERNS.items()}

def profile(text: str) -> dict:
    """Return per-text statistics used to characterize 'voice'."""
    tokens = tokenize(text)
    total = len(tokens)
    if total == 0:
        return {"total_words": 0, "unique_words": 0, "ttr": 0.0,
                "hapax": 0, "avg_word_len": 0.0, "function_word_ratio": 0.0,
                "emodern_density": 0.0, "liahona_terms": {}}
    freqs = Counter(tokens)
    unique = len(freqs)
    hapax = sum(1 for c in freqs.values() if c == 1)
    emodern = markered_density(text)
    return {
        "total_words": total,
        "unique_words": unique,
        "ttr": unique / total,
        "hapax": hapax,
        "hapax_ratio": hapax / total,
        "avg_word_len": sum(len(t) for t in tokens) / total,
        "function_word_ratio": sum(freqs[w] for w in FUNCTION_WORDS) / total,
        "emodern_density": emodern["density"],
        "liahona_terms": liahona_term_counts(text),
    }

def cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Cosine similarity between two {word: count} frequency maps."""
    common = set(vec_a) & set(vec_b)
    dot = sum(vec_a[w] * vec_b[w] for w in common)
    norm_a = sum(v * v for v in vec_a.values()) ** 0.5
    norm_b = sum(v * v for v in vec_b.values()) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)

def distinctive_words(a: Counter, b: Counter, top: int = 50) -> list[dict]:
    """Words used much more frequently in text A than text B (by rate)."""
    tot_a = sum(a.values())
    tot_b = sum(b.values())
    if tot_a == 0 or tot_b == 0:
        return []
    ratios = {}
    for w, c in a.items():
        if c < 2:
            continue
        rate_a = c / tot_a
        rate_b = b.get(w, 0) / tot_b
        ratios[w] = rate_a / (rate_b + 1e-9)
    ranked = sorted(ratios.items(), key=lambda kv: -kv[1])[:top]
    return [{"word": w, "rate_a": a[w] / tot_a, "rate_b": b.get(w, 0) / tot_b} for w, _ in ranked]

def compare_texts(name_a: str, text_a: str, name_b: str, text_b: str, top: int = 50) -> dict:
    ca, cb = word_counts(text_a), word_counts(text_b)
    pa, pb = profile(text_a), profile(text_b)
    return {
        "texts": [name_a, name_b],
        "cosine_similarity": cosine_similarity(ca, cb),
        "profiles": {name_a: pa, name_b: pb},
        "distinctive_a_over_b": distinctive_words(ca, cb, top),
        "distinctive_b_over_a": distinctive_words(cb, ca, top),
    }

