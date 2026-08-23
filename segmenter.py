"""Structural segmentation of the 1830 Book of Mormon text.

Replaces two previously-broken heuristics: analysis.py's hardcoded
"Very approximate" character-offset slicing (`bom_raw[:6548*40]`), and
bookcli.py's all-caps-line heading detection (which misattributed the sole
"Liahona" occurrence to a `None` book bucket). Both are replaced here with a
real parser built on the text's own structure: a Contents block listing
canonical heading strings, matching in-body section headings appearing again
later in the document, and verse markers in two coexisting printed formats
("37:38 ..." for most books; "3 Nephi 11:2 " / "4 Nephi 1:1 " for the two
books whose own names look like a leading number).
"""
from __future__ import annotations

import re

# Canonical 15 books of the Book of Mormon, in canonical order, mapped from
# short name to the exact heading text as printed in the Gutenberg #17
# text's Contents block (verified directly against
# texts/book_of_mormon_1830.txt).
BOM_BOOKS: list[tuple[str, str]] = [
    ("1 Nephi", "THE FIRST BOOK OF NEPHI HIS REIGN AND MINISTRY"),
    ("2 Nephi", "THE SECOND BOOK OF NEPHI"),
    ("Jacob", "THE BOOK OF JACOB"),
    ("Enos", "THE BOOK OF ENOS"),
    ("Jarom", "THE BOOK OF JAROM"),
    ("Omni", "THE BOOK OF OMNI"),
    ("Words of Mormon", "THE WORDS OF MORMON"),
    ("Mosiah", "THE BOOK OF MOSIAH"),
    ("Alma", "THE BOOK OF ALMA"),
    ("Helaman", "THE BOOK OF HELAMAN"),
    ("3 Nephi", "THIRD BOOK OF NEPHI"),
    ("4 Nephi", "FOURTH NEPHI"),
    ("Mormon", "THE BOOK OF MORMON"),
    ("Ether", "THE BOOK OF ETHER"),
    ("Moroni", "THE BOOK OF MORONI"),
]

END_MARKER_RE = re.compile(r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK", re.IGNORECASE)

# Canonical total verse count for the Book of Mormon (~6,604). Used as a
# self-check so a mis-segmentation fails loudly instead of silently
# producing a plausible-looking but wrong index -- which is exactly what
# happened previously (the sole Liahona verse dropped into a `null` bucket
# with no error).
EXPECTED_VERSE_COUNT_RANGE = (6300, 6700)


def parse_contents(text: str) -> list[str]:
    """Return the heading strings listed in the text's own Contents block,
    in order, as printed. Used to sanity-check BOM_BOOKS stays in sync with
    the source file rather than silently drifting.
    """
    match = re.search(r"^Contents\s*$", text, re.MULTILINE)
    if not match:
        raise ValueError("No 'Contents' heading found in text")
    lines = text[match.end():].splitlines()
    headings = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if headings:
                break
            continue
        if stripped != stripped.upper():
            break
        headings.append(stripped)
    return headings


def find_book_boundaries(text: str) -> list[tuple[str, int]]:
    """Return [(short_name, start_offset), ...] for each canonical book, in
    canonical order, using the LAST occurrence of each book's heading text
    as its real in-body boundary. A book's real heading may carry a
    parenthetical short-name suffix (only 1 Nephi's does in this edition,
    e.g. "...MINISTRY (1 Nephi)"), which the pattern tolerates but doesn't
    require.
    """
    boundaries = []
    for short_name, heading_text in BOM_BOOKS:
        pattern = re.compile(
            rf"^[ \t]*{re.escape(heading_text)}(?:[ \t]*\([^)]*\))?[ \t]*$",
            re.MULTILINE,
        )
        matches = list(pattern.finditer(text))
        if not matches:
            raise ValueError(f"Heading for {short_name!r} not found: {heading_text!r}")
        # The Contents-block listing (and, for "Mormon", the title page) is
        # always earlier in the document than the real in-body heading, so
        # the last match is the real section start.
        boundaries.append((short_name, matches[-1].start()))
    return boundaries


def split_into_books(text: str) -> dict[str, str]:
    """Slice raw text into {short_name: book_text}. The final book runs to
    the Project Gutenberg end marker (or end of text if absent).
    """
    boundaries = find_book_boundaries(text)
    end_match = END_MARKER_RE.search(text)
    text_end = end_match.start() if end_match else len(text)
    books = {}
    for i, (short_name, start) in enumerate(boundaries):
        stop = boundaries[i + 1][1] if i + 1 < len(boundaries) else text_end
        books[short_name] = text[start:stop]
    return books


# Matches either "37:38 ..." (bare form, used by most books) or
# "3 Nephi 11:2 ..." / "4 Nephi 1:1 ..." (full form, used only for the two
# books whose own short name starts with a number, to disambiguate). Both
# forms print chapter/verse numbers explicitly at line start, so no
# inference is needed beyond matching the two known shapes.
VERSE_RE = re.compile(
    r"^(?:(?:\d\s)?[A-Z][a-z]+(?:\s[A-Z][a-z]+)*\s)?(\d+):(\d+)\s",
    re.MULTILINE,
)


def parse_verses(book_text: str) -> list[dict]:
    """Split a single book's text into verses using VERSE_RE. Returns
    [{"chapter": int, "verse": int, "text": str}, ...] in document order.
    """
    matches = list(VERSE_RE.finditer(book_text))
    verses = []
    for i, m in enumerate(matches):
        start = m.end()
        stop = matches[i + 1].start() if i + 1 < len(matches) else len(book_text)
        verses.append({
            "chapter": int(m.group(1)),
            "verse": int(m.group(2)),
            "text": book_text[start:stop].strip(),
        })
    return verses


def build_index(text: str) -> dict:
    """Build {book: {chapter: {verse: text}}} for the whole Book of Mormon.

    Raises ValueError if the total parsed verse count falls outside
    EXPECTED_VERSE_COUNT_RANGE -- a mis-segmentation should fail loudly
    rather than silently produce a wrong-but-plausible-looking index.
    """
    books = split_into_books(text)
    index: dict = {}
    total_verses = 0
    for short_name, book_text in books.items():
        chapters: dict = {}
        for v in parse_verses(book_text):
            chapters.setdefault(v["chapter"], {})[v["verse"]] = v["text"]
            total_verses += 1
        index[short_name] = chapters
    if not (EXPECTED_VERSE_COUNT_RANGE[0] <= total_verses <= EXPECTED_VERSE_COUNT_RANGE[1]):
        raise ValueError(
            f"Parsed {total_verses} verses, expected within "
            f"{EXPECTED_VERSE_COUNT_RANGE}; segmentation is likely broken."
        )
    return index


# "Mosiah priority" -- the widely-supported theory (based on the original
# 1829 dictation manuscript's physical/textual evidence, e.g. Royal Skousen's
# critical-text work) that the Book of Mormon was dictated Mosiah-through-
# Moroni FIRST, then 1 Nephi-through-Words of Mormon LAST, to replace the
# lost 116 pages of the original "Book of Lehi." This lets any term's
# distribution be read against dictation order, not just final book order --
# e.g. checking whether "Liahona" only appears in material dictated before
# or after the passages that describe the object without using that name.
DICTATION_BATCH: dict[str, str] = {
    "Mosiah": "first", "Alma": "first", "Helaman": "first", "3 Nephi": "first",
    "4 Nephi": "first", "Mormon": "first", "Ether": "first", "Moroni": "first",
    "1 Nephi": "second", "2 Nephi": "second", "Jacob": "second", "Enos": "second",
    "Jarom": "second", "Omni": "second", "Words of Mormon": "second",
}


def by_dictation_batch(distribution: dict) -> dict:
    """Aggregate a term_distribution() result by dictation batch (see
    DICTATION_BATCH) instead of by book -- e.g. to check whether a name
    coined in the first-dictated material was reused, or avoided, in the
    later-dictated material that was ultimately placed earlier in the book.
    """
    totals = {"first": 0, "second": 0}
    books_by_batch = {"first": {}, "second": {}}
    for book, info in distribution["by_book"].items():
        batch = DICTATION_BATCH[book]
        totals[batch] += info["total"]
        books_by_batch[batch][book] = info["total"]
    return {"term": distribution["term"], "totals": totals, "books_by_batch": books_by_batch}


def term_distribution(index: dict, term: str) -> dict:
    """Per-book, per-chapter occurrence counts of `term` (case-insensitive,
    whole-word) across a built index. Replaces both of the previous broken
    heuristics (analysis.py's hardcoded character-offset slicing and
    bookcli.py's all-caps-heading detection).
    """
    needle = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
    by_book: dict = {}
    total = 0
    for book, chapters in index.items():
        book_total = 0
        by_chapter = {}
        for chapter, verses in chapters.items():
            chapter_hits = sum(len(needle.findall(v)) for v in verses.values())
            if chapter_hits:
                by_chapter[chapter] = chapter_hits
                book_total += chapter_hits
        if book_total:
            by_book[book] = {"total": book_total, "by_chapter": by_chapter}
            total += book_total
    return {"term": term, "total": total, "by_book": by_book}
