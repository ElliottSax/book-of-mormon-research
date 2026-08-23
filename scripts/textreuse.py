"""Word-level n-gram overlap detection for text reuse analysis.

Previously used character-level n-grams (5-char shingles), which is
analytically weak for this purpose: short character shingles like " the "
are common substrings of almost any English text and dominate the
"top overlaps" ranking regardless of whether two texts actually share any
real phrases. Word-level n-grams (default: 6-word sliding windows) surface
genuine shared phrasing instead.
"""
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import stylometry


def word_ngrams(text: str, n: int = 6) -> List[str]:
    """Generate word-level n-grams (as space-joined strings) from text."""
    tokens = stylometry.tokenize(text)
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def jaccard_similarity(grams_a: List[str], grams_b: List[str]) -> float:
    """Whole-corpus Jaccard similarity between two n-gram sets. A single
    summary number for how much of each text's n-gram vocabulary the other
    text shares -- complements top_overlaps' specific-phrase list.
    """
    set_a, set_b = set(grams_a), set(grams_b)
    if not set_a and not set_b:
        return 0.0
    union = set_a | set_b
    intersection = set_a & set_b
    return len(intersection) / len(union) if union else 0.0


def top_overlaps(text_a: str, text_b: str, n: int = 6, top_k: int = 20) -> List[Tuple[str, float]]:
    """Find the top-k shared word n-grams between two texts, ranked by the
    minimum occurrence-rate in either text (so a phrase common in both,
    not just frequent in one, ranks highest).
    """
    grams_a = word_ngrams(text_a, n)
    grams_b = word_ngrams(text_b, n)

    count_a = Counter(grams_a)
    count_b = Counter(grams_b)

    common = set(count_a) & set(count_b)
    overlaps = []
    for g in common:
        ratio_a = count_a[g] / len(grams_a)
        ratio_b = count_b[g] / len(grams_b)
        overlaps.append((g, min(ratio_a, ratio_b)))

    return sorted(overlaps, key=lambda x: -x[1])[:top_k]


def reuse_report(name_a: str, text_a: str, name_b: str, text_b: str, n: int = 6, top_k: int = 20) -> Dict:
    return {
        "texts": [name_a, name_b],
        "n": n,
        "jaccard_similarity": jaccard_similarity(word_ngrams(text_a, n), word_ngrams(text_b, n)),
        "top_overlaps": top_overlaps(text_a, text_b, n=n, top_k=top_k),
    }


if __name__ == "__main__":
    import json

    repo = Path(__file__).resolve().parent.parent
    reports_dir = repo / "reports"
    reports_dir.mkdir(exist_ok=True)

    bom = (repo / "texts" / "book_of_mormon_1830.txt").read_text(encoding="utf-8", errors="replace")
    spalding = (repo / "texts" / "spalding_manuscript.txt").read_text(encoding="utf-8", errors="replace")
    lahontan = (repo / "texts" / "lahontan_new_voyages.txt").read_text(encoding="utf-8", errors="replace")

    spalding_report = reuse_report("book_of_mormon", bom, "spalding_manuscript", spalding)
    (reports_dir / "textreuse_bom_vs_spalding.json").write_text(
        json.dumps(spalding_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(spalding_report, indent=2, ensure_ascii=False))

    # This pair has never been run before -- no prior report checked for
    # genuine shared multi-word phrasing between the Book of Mormon and
    # Lahontan's New Voyages.
    lahontan_report = reuse_report("book_of_mormon", bom, "lahontan_new_voyages", lahontan)
    (reports_dir / "textreuse_bom_vs_lahontan.json").write_text(
        json.dumps(lahontan_report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(lahontan_report, indent=2, ensure_ascii=False))
