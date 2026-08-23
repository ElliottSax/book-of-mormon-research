"""Corpus manager for Book of Mormon authorship research.

Provides:
1. Text loading for primary sources:
   - Book of Mormon (standard 1830 text)
   - Spalding 'Manuscript Story' (public domain text)
   - Lahontan 'New Voyages to North America' (archival text)
   - Additional candidate texts
2. Normalization utilities.
3. Simple helper to detect version mismatches (e.g., Lahonta/Liahona).
"""
import re
from pathlib import Path
from typing import List, Dict

# ----------------------------------------------------------------------
# Source locations - preferentially load from disk, otherwise fall back to URLs
# ----------------------------------------------------------------------
from urllib.request import urlopen

def _url_to_text(url: str) -> str:
    """Fetch raw text from a URL (UTF-8 decoded)."""
    try:
        with urlopen(url) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset)
    except Exception as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")

# Primary corpus files (already downloaded manually)
REPO_ROOT = Path(__file__).resolve().parent
DATA_DIR = REPO_ROOT / "texts"

# Book of Mormon (Project Gutenberg 1964 edition)
BOM_PATH = DATA_DIR / "book_of_mormon_1830.txt"

# Spalding manuscript (Project Gutenberg style text)
SPALDING_PATH = DATA_DIR / "spalding_manuscript.txt"

# Lahontan New Voyages - look for known identifier
LAHONTAN_PATH = DATA_DIR / "lahontan_new_voyages.txt"

# Aeneid (control/baseline text - unrelated genre and period, used to sanity
# check that high similarity scores aren't just "any two old-fashioned texts
# look similar")
AENEID_PATH = DATA_DIR / "aeneid.txt"

# Fallback URLs if a file is missing locally. These point at stable Project
# Gutenberg plain-text mirrors rather than archive.org identifiers that may
# not exist (the previous entries here were unverified guesses).
FALLBACK_URLS = {
    "book_of_mormon_1830.txt": "https://www.gutenberg.org/cache/epub/17/pg17.txt",
    "lahontan_new_voyages.txt": "https://www.gutenberg.org/cache/epub/56728/pg56728.txt",
    "spalding_manuscript.txt": "https://www.gutenberg.org/cache/epub/47461/pg47461.txt",
    "aeneid.txt": "https://www.gutenberg.org/cache/epub/228/pg228.txt",
}

# Minimum word count for a loaded text to be considered plausibly real.
# Chosen well below the shortest genuine corpus text (~44k words) so it only
# catches obviously-wrong content (error pages, empty downloads), not
# legitimately short texts.
MIN_PLAUSIBLE_WORDS = 1000

# Substrings that indicate a "text" file is actually a saved HTTP error page
# or similar download failure rather than real content. This is not a
# hypothetical: texts/aeneid.txt and texts/aeneid_dryden.txt were both found
# to be exactly this (a saved archive.org error page and a raw 504 Gateway
# Time-out page, respectively).
CORRUPTION_MARKERS = (
    "<!doctype html",
    "<html",
    "internet archive: error",
    "gateway time-out",
    "504 gateway",
    "403 forbidden",
    "404 not found",
)


class CorruptTextError(RuntimeError):
    """Raised when a loaded 'text' file is actually a download-failure artifact."""


def verify_text_integrity(name: str, text: str) -> None:
    """Raise CorruptTextError if `text` looks like a saved error page/download
    failure rather than real corpus content, instead of letting it pass
    silently into every downstream analysis.
    """
    lowered = text.lower()
    for marker in CORRUPTION_MARKERS:
        if marker in lowered[:2000]:
            raise CorruptTextError(
                f"'{name}' looks like a download-failure artifact "
                f"(matched marker {marker!r}), not real text."
            )
    word_count = len(text.split())
    if word_count < MIN_PLAUSIBLE_WORDS:
        raise CorruptTextError(
            f"'{name}' has only {word_count} words (< {MIN_PLAUSIBLE_WORDS}); "
            "too short to be a genuine corpus text."
        )


def load_text(path: Path) -> str:
    """Load text from a local file. If missing, fetch from fallback URL."""
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    else:
        url = FALLBACK_URLS.get(path.name)
        if not url:
            raise FileNotFoundError(f"No text at {path} and no fallback URL")
        txt = _url_to_text(url)
        # Cache to disk for future runs
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(txt, encoding="utf-8")
        return txt

def normalize_spacing(text: str) -> str:
    """Collapse whitespace and fix double-newlines common in OCR scans."""
    text = re.sub(r"\r\n|\r|\n{3,}", "\n\n", text)  # Normalize line breaks
    text = re.sub(r"\n{2,}", "\n\n", text)        # Collapse multiple blank lines
    text = re.sub(r"\s+", " ", text)              # Collapse spaces
    return text.strip()

def get_all_texts() -> Dict[str, str]:
    """Return a dict of named texts keyed by source identifier.

    Every text is passed through verify_text_integrity() before being
    returned, so a corrupted download (an HTML error page saved as .txt,
    an empty file, etc.) raises loudly here instead of silently propagating
    into every downstream analysis.
    """
    sources = {
        "book_of_mormon": BOM_PATH,
        "spalding_manuscript": SPALDING_PATH,
        "lahontan_new_voyages": LAHONTAN_PATH,
        "aeneid": AENEID_PATH,
    }
    texts = {}
    for name, path in sources.items():
        text = normalize_spacing(load_text(path))
        verify_text_integrity(name, text)
        texts[name] = text
    return texts

def detect_liahona_spelling(text: str) -> List[str]:
    """
    Detect instances of 'Lehonti' or 'Liahona' in raw text.
    Returns matches so we can check manuscript spelling variations.
    """
    pattern = r"\b(Liah?a?ona|Leh?onti)\b"
    return re.findall(pattern, text, flags=re.IGNORECASE)