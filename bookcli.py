#!/usr/bin/env python3
"""Bookcli — command-line interface for the Book of Mormon authorship research engine.

Subcommands:
  search <text> <query>     Contextual phrase search within a corpus text.
  compare <a> <b>           Stylometric comparison of two corpus texts.
  overlap <a> <b>           Character n-gram (shingle) reuse detection.
  names <a> <b>             Proper-noun (onomasticon) overlap between two texts.
  markers <text>            EMODERN / KJV-dialect marker density analysis.
  segment <text> --term T   Per-book distribution of a term (e.g. Liahona).
  report                    Run the full pipeline and write reports/authorship_analysis.json.

Corpus identifiers: book_of_mormon, spalding_manuscript, lahontan_new_voyages, aeneid.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

import corpus
import stylometry
import textreuse
import onomasticon_match
import segmenter
import namesim
import parody_hypotheses

TEXTS = ("book_of_mormon", "spalding_manuscript", "lahontan_new_voyages", "aeneid")


def _load_all() -> dict[str, str]:
    return corpus.get_all_texts()


def _require(name: str, texts: dict[str, str]) -> str:
    if name not in texts:
        sys.exit(f"Unknown text '{name}'. Available: {', '.join(sorted(texts))}")
    return texts[name]


def cmd_search(args: argparse.Namespace) -> None:
    texts = _load_all()
    raw = texts[args.text]
    # Work on the normalized text but preserve case for display.
    haystack = corpus.normalize_spacing(raw)
    query = args.query
    lowered = haystack.lower()
    needle = query.lower()
    hits = [m.start() for m in re.finditer(re.escape(needle), lowered)]
    if not hits:
        print(f"No occurrences of '{query}' in {args.text}.")
        return
    print(f"{len(hits)} occurrence(s) of '{query}' in {args.text}:\n")
    window = args.window
    for i, start in enumerate(hits[: args.limit]):
        s = max(0, start - window)
        e = min(len(haystack), start + len(needle) + window)
        snippet = re.sub(r"\s+", " ", haystack[s:e])
        print(f"  [{i + 1}] ...{snippet}...\n")


def cmd_compare(args: argparse.Namespace) -> None:
    texts = _load_all()
    a = _require(args.a, texts)
    b = _require(args.b, texts)
    result = stylometry.compare_texts(args.a, a, args.b, b, args.top)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def cmd_overlap(args: argparse.Namespace) -> None:
    texts = _load_all()
    a = _require(args.a, texts)
    b = _require(args.b, texts)
    result = textreuse.reuse_report(args.a, a, args.b, b, n=args.n, top_k=args.top)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8",
        )


def cmd_names(args: argparse.Namespace) -> None:
    texts = _load_all()
    a = _require(args.a, texts)
    b = _require(args.b, texts)
    result = onomasticon_match.match(a, b)
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_markers(args: argparse.Namespace) -> None:
    texts = _load_all()
    text = _require(args.text, texts)
    result = {
        "text": args.text,
        "profile": stylometry.profile(text),
        "marker_density": stylometry.markered_density(text),
        "liahona_terms": stylometry.liahona_term_counts(text),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def cmd_segment(args: argparse.Namespace) -> None:
    """Per-book, per-chapter distribution of a term in the Book of Mormon.

    Uses segmenter.py's real Contents-block/verse-marker parser, not a
    heading-line heuristic -- the previous all-caps-line detector
    misattributed the sole "Liahona" occurrence to a `None` book bucket.
    """
    if args.text != "book_of_mormon":
        sys.exit("segment currently only supports 'book_of_mormon' "
                  "(the only corpus text with parseable book/chapter/verse structure).")
    raw = corpus.load_text(corpus.BOM_PATH)
    index = segmenter.build_index(raw)
    result = segmenter.term_distribution(index, args.term)
    print(f"Distribution of '{args.term}' by book/chapter ({result['total']} total):\n")
    for book, info in result["by_book"].items():
        print(f"  {book}: {info['total']} ({info['by_chapter']})")
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8",
        )


def cmd_namesim(args: argparse.Namespace) -> None:
    texts = _load_all()
    against = _require(args.against, texts)
    population = namesim.distinctive_name_population(against)

    if args.batch:
        results = []
        for h in parody_hypotheses.HYPOTHESES:
            evaluation = namesim.evaluate_candidate_pair(h["name_a"], h["name_b"], population)
            results.append({"hypothesis_id": h["id"], "claim": h["claim"], "evaluation": evaluation})
        print(json.dumps(results, indent=2, ensure_ascii=False))
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
        return

    if not args.name_a or not args.name_b:
        sys.exit("namesim requires name_a and name_b (or pass --batch to evaluate the hypothesis registry).")

    result = namesim.evaluate_candidate_pair(args.name_a, args.name_b, population)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_report(args: argparse.Namespace) -> None:
    sys.path.insert(0, str(REPO))
    import analysis
    analysis.run_analysis()


def main() -> None:
    parser = argparse.ArgumentParser(prog="bookcli", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Contextual phrase search")
    p_search.add_argument("text", choices=TEXTS)
    p_search.add_argument("query")
    p_search.add_argument("--window", type=int, default=80, help="characters each side")
    p_search.add_argument("--limit", type=int, default=20)
    p_search.set_defaults(func=cmd_search)

    p_compare = sub.add_parser("compare", help="Stylometric comparison")
    p_compare.add_argument("a", choices=TEXTS)
    p_compare.add_argument("b", choices=TEXTS)
    p_compare.add_argument("--top", type=int, default=50)
    p_compare.add_argument("--json-out")
    p_compare.set_defaults(func=cmd_compare)

    p_overlap = sub.add_parser("overlap", help="Word-level n-gram reuse detection")
    p_overlap.add_argument("a", choices=TEXTS)
    p_overlap.add_argument("b", choices=TEXTS)
    p_overlap.add_argument("--n", type=int, default=6, help="n-gram length in WORDS (not characters)")
    p_overlap.add_argument("--top", type=int, default=20)
    p_overlap.add_argument("--json-out")
    p_overlap.set_defaults(func=cmd_overlap)

    p_names = sub.add_parser("names", help="Proper-noun overlap")
    p_names.add_argument("a", choices=TEXTS)
    p_names.add_argument("b", choices=TEXTS)
    p_names.set_defaults(func=cmd_names)

    p_markers = sub.add_parser("markers", help="EMODERN marker density")
    p_markers.add_argument("text", choices=TEXTS)
    p_markers.add_argument("--json-out")
    p_markers.set_defaults(func=cmd_markers)

    p_segment = sub.add_parser("segment", help="Per-book/chapter term distribution (book_of_mormon only)")
    p_segment.add_argument("text", choices=("book_of_mormon",))
    p_segment.add_argument("--term", required=True)
    p_segment.add_argument("--json-out")
    p_segment.set_defaults(func=cmd_segment)

    p_namesim = sub.add_parser("namesim", help="Name-derivation similarity vs. a chance baseline")
    p_namesim.add_argument("name_a", nargs="?", help="required unless --batch")
    p_namesim.add_argument("name_b", nargs="?", help="required unless --batch")
    p_namesim.add_argument("--against", choices=TEXTS, required=True,
                            help="corpus text to draw the baseline vocabulary population from")
    p_namesim.add_argument("--batch", action="store_true",
                            help="evaluate every hypothesis in parody_hypotheses.HYPOTHESES instead of one pair")
    p_namesim.add_argument("--json-out")
    p_namesim.set_defaults(func=cmd_namesim)

    p_report = sub.add_parser("report", help="Run full analysis pipeline")
    p_report.set_defaults(func=cmd_report)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
