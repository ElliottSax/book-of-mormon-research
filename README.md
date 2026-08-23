# Book of Mormon Authorship Research

A skeptical, multi-angle analytics toolkit for testing Book of Mormon
authorship hypotheses: stylometric comparison against candidate source
texts, proper-noun overlap, word-level text-reuse detection, real
book/chapter/verse structural segmentation, and a name-derivation
similarity checker with a mandatory chance-baseline comparison built in.

See **[RESEARCH_LOG.md](RESEARCH_LOG.md)** for the current state of
findings — what's been tested, what was found, and how confident to be
about it. Start there before re-running analyses from scratch.

## Quickstart

```bash
pip install -e .[dev]        # installs jellyfish + pytest
python -m pytest -q          # run the test suite
python bookcli.py report     # run the full pipeline -> reports/authorship_analysis.json
```

## Corpus

| Text | Identifier | Source | Integrity |
|---|---|---|---|
| Book of Mormon (1830 text) | `book_of_mormon` | Project Gutenberg #17 | verified |
| Spalding "Manuscript Story" | `spalding_manuscript` | Oberlin College copy (public domain) | verified |
| Lahontan, *New Voyages to North-America* | `lahontan_new_voyages` | Thwaites 1905 critical edition, Vol. I + II (archive.org) | verified |
| Aeneid (control text) | `aeneid` | Dryden translation, Project Gutenberg #228 | verified |

Every text is checked by `corpus.verify_text_integrity()` on load — it
raises loudly on the corruption class found during this repo's initial
audit (saved HTML error pages, timeout pages, or implausibly short text)
rather than letting it silently pass into analysis. See RESEARCH_LOG.md
for why the Aeneid and Lahontan texts specifically needed re-sourcing.

`research-notes/` holds supporting material that isn't corpus text to be
analyzed programmatically — currently the user's own prior Liahona/Lahontan
research dossier (`liahona_dossier.docx` + a plain-text extraction),
cited throughout `RESEARCH_LOG.md` and `parody_hypotheses.py`.

## CLI (`bookcli.py`)

```
search <text> <query>              Contextual phrase search within a corpus text.
compare <a> <b>                    Stylometric comparison of two corpus texts.
overlap <a> <b>                    Word-level n-gram (default 6-word) reuse detection.
names <a> <b>                      Proper-noun (onomasticon) overlap between two texts.
markers <text>                     EMODERN / KJV-dialect marker density analysis.
segment book_of_mormon --term T    Real per-book/chapter distribution of a term.
namesim <a> <b> --against <text>   Name-derivation similarity vs. a chance baseline.
namesim --batch --against <text>   Evaluate every hypothesis in parody_hypotheses.py.
report                             Run the full pipeline -> reports/authorship_analysis.json.
```

Corpus identifiers: `book_of_mormon`, `spalding_manuscript`,
`lahontan_new_voyages`, `aeneid`.

## Module map

- `corpus.py` — text loading, normalization, integrity verification.
- `stylometry.py` — word-frequency profiles, cosine similarity, EModern/KJV
  marker density, OCR-long-s-tolerant term counting.
- `segmenter.py` — real Book of Mormon book/chapter/verse structural parser
  (built on the text's own Contents block and verse markers, not a
  heading-line heuristic), plus dictation-order (Mosiah-priority) analysis.
- `namesim.py` — name-derivation similarity (Soundex/NYSIIS/Metaphone via
  `jellyfish`, plus sequence/Jaro-Winkler similarity) with a mandatory
  chance-baseline check against real corpus vocabulary, to guard against
  the apophenia risk inherent in soundalike-name theories.
- `parody_hypotheses.py` — citation-carrying registry of specific claims
  to test (kept separate from the scoring algorithm in `namesim.py`).
- `scripts/onomasticon_match.py` — proper-noun overlap detection, filtered
  against both common-word and Gutenberg-boilerplate false positives.
- `scripts/textreuse.py` — word-level n-gram shared-phrase detection.
- `analysis.py` — the consolidated pipeline (`bookcli.py report`) that runs
  everything above and writes `reports/authorship_analysis.json`.

## Tests

`tests/` covers `stylometry.py`, `corpus.py`, `segmenter.py`, `namesim.py`,
`scripts/textreuse.py`, and `scripts/onomasticon_match.py`, including
regression tests for specific bugs found and fixed during this repo's
initial audit (e.g. the Liahona term being misattributed to a `null` book
bucket, and the "compass"/"compassion" substring-matching conflation).
