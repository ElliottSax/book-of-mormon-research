"""Registry of name-derivation / "parody"-adjacent hypotheses to test.

Separates the CLAIMS (this file -- data, with citations) from the ALGORITHM
(namesim.py -- the scoring method), per the project's requirement to treat
the general wordplay-hypothesis framework separately from any one specific
candidate connection.

Seeded from primary research conducted 2026-08-23. See RESEARCH_LOG.md for
the full narrative writeup and skeptical verdicts; this file exists so
`bookcli.py namesim --batch` has structured claims to iterate over.
"""
from __future__ import annotations

HYPOTHESES = [
    {
        "id": "mormon_le_parasite_mormon",
        "claim": (
            "Lars Nielsen (2024) argues the name 'Mormon' derives from "
            "'Le Parasite Mormon: Histoire Comique' (1650), a French satire "
            "of a real person (Montmaur), via a claimed syllable swap "
            "mon-MOR -> MOR-mon."
        ),
        "name_a": "Mormon",
        "name_b": "Mormon",  # the claimed derivation is the TITLE reference, not a different spelling
        "source_citation": (
            "Lars Nielsen, 'How the Book of Mormon Came to Pass: The Second "
            "Greatest Show on Earth' (2024); summarized via discussmormonism.com "
            "forum discussion and religionunplugged.com book excerpt, 2026-08-23."
        ),
        "source_acquired": False,
        "note": (
            "Not a soundalike-derivation claim in the namesim.py sense (the "
            "words are identical) -- the claim is about a chain of transmission "
            "(French satire -> Kircher-adjacent milieu -> Spalding -> Rigdon -> "
            "Smith), not phonetic similarity. namesim.py isn't the right tool "
            "for this specific claim; it needs historical-transmission evidence "
            "(availability.py), not a similarity score."
        ),
    },
    {
        "id": "nephi_barachias_nephi",
        "claim": (
            "Nielsen argues 'Nephi' derives from Athanasius Kircher's "
            "'Barachias Nephi', used only in Kircher's unpublished 1628-1632 "
            "letters to Pietro della Valle (Vatican archives) -- Kircher's "
            "PUBLISHED works instead say 'Abenephius the Arab', a discrepancy "
            "critics have flagged as a factual problem with the sourcing."
        ),
        "name_a": "Nephi",
        "name_b": "Nephi",
        "source_citation": (
            "Interpreter Foundation review, 'The Flimsiest Show on Earth' "
            "(interpreterfoundation.org/journal/the-flimsiest-show-on-earth), "
            "accessed 2026-08-23; also notes 'Nephi' independently appears in "
            "the Book of Judges (per a forum commenter) as an existing "
            "alternative, non-Kircher explanation."
        ),
        "source_acquired": False,
        "note": (
            "Same caveat as above: this is a claimed transmission-chain, not "
            "a soundalike pair. Also worth weighing the independent "
            "biblical-name explanation (Judges) as a simpler alternative."
        ),
    },
    {
        "id": "liahona_lahontan",
        "claim": (
            "The repo owner's own prior research (a ~81,000-word dossier, "
            "reviewed 2026-08-23, predating this codebase) argues for a "
            "Lahontan/Liahona connection on three legs: (a) phonetic -- the "
            "Book of Mormon's original manuscript spelling 'Lahonti' "
            "(later editorially changed to 'Lehonti', Alma 47) is one letter "
            "from 'Lahontan', and 'Liahona' itself shares the consonant "
            "skeleton L-H-N with a documented period variant spelling "
            "'La Hontan'; (b) conceptual -- Lahontan's New Voyages Vol. II "
            "describes indigenous peoples attributing spiritual agency to a "
            "compass and other instruments (quoted below), thematically "
            "adjacent to the Liahona's faith-dependent operation (Alma "
            "37:40); (c) access -- Lahontan's English translation is "
            "documented in Jefferson's library and the Library Company of "
            "Philadelphia, though explicitly NOT in the Manchester/Palmyra "
            "library nearest Joseph Smith himself (per Robert Paul's 1982 "
            "study) -- a negative finding the dossier reports honestly."
        ),
        "name_a": "Liahona",
        "name_b": "Lahontan",
        "source_citation": (
            "User's own research dossier (research-notes/liahona_dossier.docx, "
            "reviewed 2026-08-23), citing: Thwaites's 1905 critical edition "
            "of Lahontan (Vol. II, p.~10305: 'The Savages believe that a "
            "Watch, a Compass, and a thousand other Machines are moved by "
            "Spirits'; and p.~849: 'They took my Graphometer for somewhat "
            "Divine... without there were some Supernatural Assistance'); "
            "Robert Paul (1982) on the Manchester library holdings; Skousen's "
            "Critical Text Project for the original-manuscript 'Lahonti' "
            "spelling. No PUBLISHED secondary source (Nielsen or otherwise) "
            "connects Lahontan to Liahona -- this is an original hypothesis, "
            "not documented existing scholarship, and the dossier's own "
            "verdict (Part XVII.4) is explicitly 'no slam dunk either way'."
        ),
        "source_acquired": True,  # texts/lahontan_new_voyages.txt now includes both Thwaites volumes
        "note": (
            "IMPORTANT CORRECTION (2026-08-23): an earlier pass through this "
            "codebase concluded a lexical NULL result (zero 'compass'/"
            "'liahona' occurrences in Lahontan) -- that was wrong on two "
            "counts: (1) the corpus text only had Volume I; the passages "
            "above are in Volume II, which was entirely missing until this "
            "correction; (2) the OCR renders long-s as 'f' ('compass' scans "
            "as 'compafs'/'compaff'), so literal-string search undercounted "
            "even within Volume I. Both are now fixed (see "
            "stylometry.ocr_tolerant_pattern, and texts/lahontan_new_voyages.txt "
            "now concatenates Thwaites Vol. I + II). "
            "CORRECTED COUNT: manually disambiguated (regex can't "
            "distinguish the instrument noun from the archaic verb 'to "
            "compass'=achieve, or the noun sense 'compass'=extent/range), "
            "'compass' appears 26 times total in the OCR-tolerant automated "
            "count, of which 7 are genuinely the navigational-instrument "
            "sense -- 13 are the verb ('compass their end'), 6 are the "
            "'extent/range' noun sense. Of those 7 instrument-sense hits, "
            "ONE is the passage quoted above ('a Watch, a Compafs... moved "
            "by Spirits') -- a genuine, specific, quotable conceptual "
            "parallel, not a coincidental false positive like 'ball'/"
            "'director'. 'ball' remains a genuine null even in the complete "
            "text: all 26 occurrences are gunpowder/ammunition, a cannonball, "
            "a watermelon simile, or a description of an indigenous ball "
            "game (lacrosse) -- none relate to a guidance device. Stay "
            "skeptical of the passage's framing: it is Lahontan's own mocking, "
            "skeptical aside about 'ignorant' natives misunderstanding "
            "European technology, not a reverent account -- a real tonal gap "
            "from the Book of Mormon's first-person treatment of the "
            "Liahona. No evidence has been found that Joseph Smith, Spalding, "
            "or Rigdon actually read this specific passage; availability is "
            "necessary but not sufficient. See RESEARCH_LOG.md for the full "
            "writeup and namesim.py's baseline-checked orthographic score."
        ),
    },
]


def get(hypothesis_id: str) -> dict:
    for h in HYPOTHESES:
        if h["id"] == hypothesis_id:
            return h
    raise KeyError(f"No hypothesis with id {hypothesis_id!r}")
