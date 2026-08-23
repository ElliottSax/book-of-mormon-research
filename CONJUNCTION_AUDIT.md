# Conjunction Audit: Requirements vs. Evidence

## Why this document exists

The user's own prior dossier (`research-notes/liahona_dossier.docx`, Part
XIX) flags a problem it admits it never finished addressing: every time a
new supporting detail gets added to a source-theory case — a library
holding, a phonetic resemblance, a functional parallel — it's tempting to
treat it as one more brick making the wall stronger. But if these details
are actually **necessary links that all have to be true simultaneously**
for a causal chain to hold, then adding more of them multiplies the joint
probability **down**, not up. A wall gets stronger with more bricks, even
redundant ones. A chain is only as strong as its weakest link, and its
overall odds are the *product* of every link's odds, not a sum or a pile.

This document does the sorting work the dossier flagged as unfinished:
separating every claim this project has gathered (across `RESEARCH_LOG.md`)
into **independent evidence** (true/false on its own merits, doesn't need
anything else to be true) versus **required links** (must ALL hold
simultaneously for a specific proposed causal chain to be the actual
explanation). Confidence ratings below are explicitly rough, qualitative,
illustrative bands — not a rigorous calculation — used only to show the
*structure* of how compounding works, not to produce a real number.

---

## A base-rate benchmark for name-similarity claims generally

Before weighing any specific phonetic-resemblance claim (Liahona/Lahontan,
Lehonti/Lahontan, or any future one), it's worth having an actual measured
base rate from the text itself, rather than judging each claim in
isolation. Ran `namesim.py` pairwise across all 378 distinctive Book of
Mormon proper nouns (71,253 pairs) extracted via `onomasticon_match`.

**Finding: incidental phonetic overlap between demonstrably unrelated BoM
entities is common, not rare.** Multiple pairs with zero narrative
connection score higher than 0.85–0.94: Messiah/Mosiah (0.927, a title vs.
a king's name), Melek/Mulek (0.936, a city vs. a person), Amaleki/Amulek
(0.930, two unconnected characters), Sidom/Sodom (0.936, a BoM city vs. the
biblical one). This is what a large invented name-vocabulary drawing on a
limited phonetic palette (recurring roots like "am-," "-oni," "-ihah")
produces by default.

**A useful positive control: Moroni/Moronihah** (a confirmed father-son
pair, explicitly stated in the text) scores **0.547**. This gives a rough
benchmark for what a *real*, textually-confirmed instance of intentional
name-reuse looks like in this scoring scheme.

**Checked against that benchmark: Lehonti/Liahona scores 0.263** — ranked
1,208th of 71,253 pairs, well below the Moroni/Moronihah benchmark and
below over a thousand other pairs in the text, most of which (per the
examples above) are coincidental. This is why the "Lahonti" spelling claim
was withdrawn above as a category error rather than just discounted — it
doesn't just lack a stated textual connection, it's also a weaker match
than the text's own standard for what real name-reuse looks like.

**Recommendation**: any future name-pair claim (Book of Mormon internal, or
against an external source) should be checked against this same benchmark
— does it clear the ~0.55 confirmed-relationship bar, or does it sit in the
0.85+ range of demonstrably-coincidental pairs, or somewhere in between? A
bare "these sound alike" observation isn't evidence on its own in a text
this large; where it lands relative to both anchors is.

---

## Chain A: Lahontan's text → the name/concept "Liahona" (direct route)

| # | Required link | Status | Rough confidence |
|---|---|---|---|
| A1 | Lahontan's Vol. II genuinely contains the compass/spirits passage | **Confirmed** (it's a fact about the text, not probabilistic) | — |
| A2 | That content was accessible to Spalding, Rigdon, or Smith before 1830 | **Weak.** "All but forgotten" in English print culture after the 1740s (modern scholarship); confirmed absent from the Manchester/Palmyra library (Robert Paul, 1982 — a real negative, not just unconfirmed); present in Jefferson's library and the Library Company of Philadelphia (elite, geographically distant access); Carver — the book actually in circulation in Smith's era — borrowed from Lahontan but demonstrably NOT the relevant passages | ~10–20% |
| A3 | Whoever accessed it specifically engaged with/remembered the compass passage (one passage in a 269,000-word two-volume work) | Unquantifiable but not implausible *conditional on A2* — it's a notable passage in a notable section | ~30–40% conditional |
| A4 | That memory was transformed into the specific name "Liahona" via some real (if unrecorded) derivation process | **Unconfirmed.** No direct evidence of a coining process. Supported only by the orthographic z-score (~3.8) — which is undercut by selection bias: this pair was tested *because* it already looked similar, the exact multiple-comparisons problem `namesim.py` was built to flag | ~15–25% |
| A5 | *(dossier's separate claim)* the original-manuscript "Lahonti" spelling is phonetic evidence | **Withdrawn — category error, not just weak.** Checked directly: "Lehonti" (Alma 47) is a Lamanite military leader poisoned by Amalickiah — a person, unrelated narratively to the Liahona object. This is a different word referring to a different entity; it doesn't bear on Liahona's etymology at all and should be removed from the case, not merely discounted | N/A — remove |

**Illustrative compounding (A2 × A3 × A4, midpoints):** 0.15 × 0.35 × 0.20 ≈
**1%**. Even treating each step charitably, the chain collapses fast — this
is the mechanism the dossier's Part XIX warned about, made concrete.

**Independent evidence that survives regardless of whether this chain
holds:** the compass/spirits passage is a real, confirmed historical
curiosity, worth knowing about on its own terms; the Gervase of Tilbury
identification is a genuine bibliographic contribution independent of any
Book of Mormon relevance; the dictation-order (Mosiah-priority) finding
about Liahona's Alma-only distribution is a self-contained observation
about the Book of Mormon's *own* internal composition, requiring no
external-source theory at all; the corrected stylometric baseline (the
Aeneid control shows BoM-vs-Lahontan isn't distinctively elevated versus
BoM-vs-an-unrelated-text) is a solid methodological result on its own.

---

## Chain B: Nielsen's Kircher chain (Kircher → Dartmouth → Spalding → Rigdon → Smith)

| # | Required link | Status | Rough confidence |
|---|---|---|---|
| B1 | Spalding-Rigdon authorship theory holds at all | **Contested** by mainstream scholarship on both critical and apologetic sides (Fawn Brodie's *No Man Knows My History* "decisively rejected" it, per the user's own dossier; the recovered Oberlin manuscript bears no resemblance to the Book of Mormon) | ~20–30%, generously |
| B2 | Kircher → John Smith (the Dartmouth professor) transmission | **Actively rebutted.** No Kircher works in Dartmouth's library catalogues, checked 1775 and 1825 (bracketing Smith's entire career); Smith's own writings state Native Americans are *not* descended from Jews — the opposite of the premise required | ~5% |
| B3 | John Smith → Spalding | Unconfirmed, no evidence beyond ordinary coursework | ~15% |

**This chain is already dead at B2** — multiplying by ~5% makes every
subsequent link's status academic. No further work on this chain is
warranted; it's resolved, not open.

---

## Chain C: Aeneid Book VI "twin doves" → Liahona "two spindles"

| # | Required link | Status | Rough confidence |
|---|---|---|---|
| C1 | Spalding attended Dartmouth, classical curriculum | **Confirmed** | — |
| C2 | Exposed to the Aeneid generally | Plausible/likely | ~70–80% |
| C3 | Specifically Book VI (not just Books 1–4, the only period-documented standard) | **Weakened.** Columbia's 1785 requirement — the one comparable contemporaneous record found — specifies the first four books only; the six-book standard is a mid-19th-century development, decades later; no Dartmouth-specific record exists either way | ~25–35% |
| C4 | Spalding-Rigdon transmission chain holds | Same as B1 — contested | ~20–30% |
| C5 | The specific "twin doves" detail (not just general Aeneid exposure) is what produced "two spindles" | **Weak.** Doves are generic, conventional Venus iconography, not a bespoke invention; twoness didn't propagate forward even in the Aeneid's own later reception (the bough, not the doves, is what recurred); the Argonautica precursor Virgil himself drew on uses a *single* dove, not two — twoness enters only at the Virgil link, nowhere else in the tradition | ~10–15% |

**Illustrative compounding (C2 × C3 × C4 × C5, midpoints):** 0.75 × 0.30 ×
0.25 × 0.12 ≈ **0.7%**.

**Eliminated, not just discounted:** the "same place in the storyline"
argument, offered as corroboration for this chain, was checked directly
against both texts and found structurally *opposite* — the doves' guidance
exists only because Aeneas's journey is already over; the Liahona *is* the
journey's navigation, land and sea, ending at arrival. The user concurred
after the direct walkthrough. This doesn't multiply the chain down further
(it was corroboration, not a strict requirement) — it simply removes a
supporting argument that no longer counts as evidence at all.

**Independent evidence regardless of chain validity:** Dartmouth's
classical curriculum is real and well-documented; the Golden Bough's
literary afterlife (Turner's painting, Frazer) is genuine literary history
worth knowing on its own; the Liahona's second spindle *is* genuinely
unexplained in the text — a real, freestanding textual puzzle no matter
which (if any) external theory eventually accounts for it.

---

## Chain D: Virgil's Brass Fly (via Lahontan/Gervase) → Liahona

Shares link A2 with Chain A (same availability bottleneck — this is really
"Chain A pointing at a different passage in the same book," not an
independently-weighted chain). Given A2's ~10–20% and that the fly passage
sits ~116 lines from the compass passage in the same essay (so encountering
one makes encountering the other nearly as likely, not an added
multiplicative requirement), this chain doesn't need its own compounding
table. Already-logged verdict stands: weaker than Chain A's core claim on
both category grounds (marvelous-brass-object legends also attach to
Albertus Magnus, Bacon, and Pope Sylvester II — not distinctively Virgil's)
and functional grounds (a protective talisman, not a guidance device) —
adds context, not case strength.

---

## Overall synthesis

This is the pattern the dossier's Part XIX predicted, now made concrete:
across this whole research arc, the number of genuinely **independent**,
freestanding pieces of evidence is small — the compass/spirits passage's
existence, the Gervase identification, the Mosiah-priority distribution
pattern, the corrected stylometric baseline. Surrounding them is a much
larger set of **required links**, most individually weak-to-moderate, that
compound down to roughly 1% or less for any of the specific proposed
transmission chains (A, B, C, D) being the actual explanation, under even
charitable per-link estimates.

**This doesn't mean "there's no connection."** It means the specific,
detailed causal *stories* proposed — Kircher-to-Smith, Aeneid-Book-VI-to-
spindles, Lahontan-book-to-name-coinage — are each individually improbable
as fully-specified chains, even though the underlying observations they're
trying to explain remain real: the Liahona's second spindle is genuinely
unexplained, there is a real (if selection-biased) orthographic resemblance
to "Lahontan," and the compass/spirits passage is a genuine curiosity. Those
observations are worth continued attention. They just haven't successfully
been hung on any one fully-worked-out causal chain yet, and piling on more
supporting detail to any single chain will keep making it weaker, not
stronger, unless that detail is independent evidence rather than another
required link.

**Recommendation going forward**: before adding any new claimed parallel to
this project's case for a specific chain, sort it into one of these two
buckets first — does it stand on its own regardless of the chain (evidence),
or does the chain need it to also be true (a link)? This is the discipline
`namesim.py`'s baseline check enforces for name-pairs specifically; this
document is the same discipline applied to the whole chain, not just one
step of it.
