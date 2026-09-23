# A Framework and Architecture for Computational Book of Mormon Studies

**Status:** design document, v0.1. Sections marked ⏳ await verification from
in-flight literature research and should not be cited until confirmed.

---

## 0. The problem this framework exists to solve

Computational authorship work on the Book of Mormon has produced mutually
contradictory results for forty-five years. Broadly ⏳(details pending
literature verification):

| Study | Method | Conclusion |
|---|---|---|
| Larsen, Rencher & Layton (1980, BYU Studies) | non-contextual word frequencies, multivariate | multiple distinct "wordprints" |
| Holmes (1992, *JRSS-A*) | vocabulary richness, PCA | one voice; consistent with Smith |
| Jockers, Witten & Criddle (2008, *LLC*) | Burrows' Delta + nearest shrunken centroid | supports Spalding–Rigdon |
| Schaalje, Fields, Roper et al. (2011–) | extended NSC, open-set critique | prior result is an artifact of closed-set design |

These are not four measurements of one quantity that happen to disagree. They
are four *different questions*, asked with designs that largely determined
their own answers. A framework worth building must explain the disagreement
structurally, not adjudicate it rhetorically.

**The core technical claim of this framework:** the Book of Mormon is written
in sustained King James pastiche, and the feature families that mainstream
attribution methods depend on — above all function-word frequency — are
precisely the features that an imitated register constrains hardest. Under
that constraint two things happen at once:

- **Between-author signal is suppressed.** Candidate authors writing (or
  imitating) the same biblical register converge toward each other.
- **Within-text register variation is amplified.** A war chapter and a sermon
  in the same book differ on these features by more than two authors writing
  the same genre typically do.

A method that does not explicitly control for this will *measure register and
report authorship*. That single failure mode is sufficient to generate all
four rows of the table above, depending only on how each study happened to
slice its data. Everything below follows from taking it seriously.

---

## 1. Methodological framework

Six layers. Each is a **gate**: work does not proceed to the next layer until
the current one is satisfied, and the gates are enforced in code rather than
recommended in prose.

### L0 — Provenance and corpus integrity

*No analysis is more trustworthy than the bytes it ran on.*

This project learned each of these the hard way, in a single working session:

- Three separate files named `aeneid.txt` were all unusable — two were saved
  HTTP error pages (an archive.org error page; a raw 504 gateway timeout), and
  the third was Pope's translation of the **Iliad**, not the Aeneid at all.
- The Lahontan corpus was missing **Volume II entirely** — the volume
  containing the one passage the research thread most depended on.
- The Lahontan OCR renders long-s as `f`, so a literal search for `compass`
  returned **zero hits** in a text that contains it seven times as `compafs`.

Requirements:

- Every text carries a **manifest**: source URI, edition and editor, publication
  date, digitization method (keyed vs. OCR), OCR engine/quality where known,
  known defects, checksum, license, and retrieval date.
- **Integrity gates run on load**, not on demand: HTML/error-page detection,
  minimum plausible length, expected-structure assertions, encoding checks.
- **Known-defect declarations drive query rewriting.** A manifest that declares
  `longs_ocr: true` causes searches over that text to expand `s`→`[sf]` at
  non-final positions automatically. Defects are handled by the framework, not
  remembered by the researcher.
- Corpora are **versioned and immutable**; results cite a corpus version.

### L1 — Stratification before analysis

*The single largest methodological gap in the existing literature.*

The Book of Mormon is not a homogeneous object, and slicing it by printed book
order — as the naive approach does — confounds at least six independent
dimensions. Any analysis must declare which strata it holds constant:

1. **Structural** — book / chapter / verse.
2. **Compositional order** — the text was dictated in a different order than it
   is printed (the "Mosiah priority" account: Mosiah→Moroni first, then
   1 Nephi→Words of Mormon last, replacing the lost 116 pages). Print order is
   *not* composition order, and any analysis assuming otherwise is measuring an
   artifact. This project already implements this as
   `segmenter.by_dictation_batch()`.
3. **Scribal stint** — different scribes took dictation at different times in
   the Original Manuscript. ⏳ Pending confirmation that stint boundaries exist
   in machine-readable form; if they do, they are both a stratification
   variable *and* a natural experiment (scribal boundaries should show no
   authorial signal if dictation was continuous).
4. **Redaction layer** — the text presents itself as an abridgment, so an
   editorial voice overlays most of it. Source-record material, abridger's
   commentary, and later additions are different objects.
5. **Register / genre** — narrative, sermon, prophecy, epistle, war account,
   genealogy, legal material. This is the dominant confound; it must be a
   controlled variable, never an uncontrolled one.
6. **Quotation status** — extended biblical quotation blocks (Isaiah chapters;
   the 3 Nephi Sermon material) are *not* authored text for attribution
   purposes and must be maskable. Leaving them in contaminates every result.

**Gate:** an experiment specification must state its stratification or be
rejected. "The whole text as printed" is not a valid stratum.

### L2 — Features

Declared per experiment, never selected after seeing results.

- Function-word frequencies (the classical choice — and the one most exposed to
  the register confound; include, but never alone).
- Character *n*-grams (robust to OCR noise and comparatively register-tolerant
  ⏳).
- POS *n*-grams (requires early-modern-tolerant tagging ⏳).
- Lexical richness — with explicit length standardization; naive richness
  measures are length-dependent and this is a known defect of at least one
  prior study ⏳.
- Domain markers this project already implements: KJV/Early-Modern marker
  density, OCR-tolerant term counts.

**Gate:** feature set is fixed in the pre-registration. Reporting the best of
several feature sets without correction is prohibited (see L4).

### L3 — Methods

- **Distance:** Burrows' Delta and variants, with **Cosine Delta** as the
  default ⏳ (reported as the strongest performer in benchmark evaluations).
- **Open-set verification, not closed-set attribution.** This is
  non-negotiable, and it is the precise point on which the 2008 result was
  attacked: a forced-choice classifier trained on candidates {A, B, C} will
  attribute a text to one of them *even when the true author is none of them*.
  The default method is therefore verification — "is this text within the
  expected variation of author X's known work?" — via the **General Imposters**
  approach ⏳, which is structurally identical to the chance-baseline logic this
  project already implements in `namesim.py`: compare the candidate against a
  pool of impostors and ask whether it wins more often than chance.
- **Rolling stylometry** ⏳ for detecting seams *within* the text — directly
  applicable to the redaction-layer question, and testable against the known
  scribal-stint and quotation-block boundaries.
- **Unsupervised** clustering / consensus trees for exploratory structure, never
  as confirmatory evidence.

**Gate:** any closed-set method must ship with an explicit rejection option and
a statement of what happens if the true author is absent from the candidate set.

### L4 — Calibration, controls, and null models

*The heart of the framework. A claim without these is not a finding.*

Every claim requires all four:

**(a) Positive control — can the method detect authorship difference that is
known to exist, in this register?**

The proposed instrument is the **King James Bible itself**. Its books have
genuinely different underlying authors, and — critically — it was produced by
six translation companies with assigned portions, giving a second, documented
boundary set. A method that cannot separate Isaiah from the Pauline epistles in
the KJV, or detect company boundaries, has no business reporting authorship
boundaries in a KJV-pastiche text. This converts the register confound from an
acknowledged caveat into a *measured quantity*.

**(b) Negative control — does the method avoid inventing boundaries that do not
exist?**

Two instruments. First, chunk a long **single-author** work and verify the
method does not split it. Second, and more pointed: the **pseudo-biblical
corpus** — the documented genre of early-American texts written in deliberate
KJV cadence (per Shalev's scholarship ⏳). These are known single authors writing
in exactly the artificial register that confounds everything. They are the
closest available analogue to the questioned text, and the most honest test of
whether any of this works at all.

**(c) Null distribution.** Permutation or bootstrap baseline for the specific
statistic, computed from the actual corpus rather than assumed. This project
has already demonstrated why: a pairwise scan of all 378 distinctive Book of
Mormon proper nouns (71,253 pairs) found that *demonstrably unrelated* names
routinely score very high — Messiah/Mosiah 0.927, Melek/Mulek 0.936 — while a
confirmed father–son pair (Moroni/Moronihah) scores 0.547. Without that
baseline, any individual "striking" resemblance is uninterpretable.

**(d) Multiplicity correction.** When *k* candidates or feature sets were tried,
report *k* and correct. The failure mode is specific and was hit repeatedly in
this project's own work: a name pair proposed *because* it already looked
similar cannot then be tested for surprising similarity without accounting for
the search that produced it.

**Gate:** results without (a)–(d) are logged as exploratory and may not be
reported as findings.

### L5 — Claims ledger and conjunction audit

*For the historical/transmission side — "and similar" analysis.*

Stylometry answers "does the text look internally heterogeneous." It does not
answer "did author X read source Y." That second question has its own failure
modes, and this project has already built the instrument for them:

- **Every claim is typed** as either **independent evidence** (stands or falls
  on its own) or a **required link** (must hold *simultaneously* with others for
  a proposed chain to work). Piling required links onto a chain multiplies its
  joint probability *down*; piling independent evidence raises confidence. The
  two are routinely conflated, and the conflation always favors the hypothesis.
- **Accessibility is a hard gate.** A transmission claim requires documented
  pre-1830 availability. This alone terminated several threads in this project:
  no English Strabo until 1854; the Rechabites narrative untranslated until
  1893; the Fenian "Crane Bag" material until 1859; Lahontan "all but forgotten"
  in English print culture after the 1740s and confirmed absent from the
  Manchester library.
- **Primary source before argument.** Verify the claimed text says what it is
  said to say, *first*. In this project: a claimed place name in Xenophon did
  not exist there; a chapter about "Zosimos" turned out to concern a different
  figure entirely; an Irish "treasurer" turned out to be the antagonist who
  killed the hero's father. Each would have supported an argument built on
  nothing.
- **Genre base rates.** Before treating a parallel as diagnostic, ask how common
  it is across the genre. "A civility gradient between a settled and a wandering
  people" and "a marvelous object of brass" are near-universal in this
  literature and diagnostic of nothing.

### L6 — Reproducibility and adversarial review

- Every reported number regenerable by one command against a cited corpus
  version.
- Schema-versioned machine-readable output (a prior integration in this repo
  silently produced empty reports for months by reading keys that never existed;
  the schema version exists to make that failure loud).
- A dated narrative log recording what was tested, the baseline it was tested
  against, and an explicit verdict — including negatives.
- **Pre-registration**: hypothesis, corpus version, strata, features, method,
  controls, and *falsification criterion* declared before the run.
- **Adversarial pass**: an independent attempt to break each surviving finding
  before publication.

---

## 2. Software architecture

```
bomsr/
  corpus/
    manifest.py        # provenance schema, checksums, defect declarations
    integrity.py       # load-time gates (error pages, length, structure)
    normalize.py       # whitespace, casing, defect-aware query rewriting
    registry/          # one manifest per text, version-controlled
  strata/
    structure.py       # book/chapter/verse parsing + self-check
    composition.py     # dictation order, scribal stints
    redaction.py       # abridgment-layer tagging
    register.py        # genre/voice tagging
    quotation.py       # biblical quotation detection and masking
  features/
    function_words.py  char_ngrams.py  pos_ngrams.py  richness.py  markers.py
  methods/
    delta.py           # Burrows / Cosine / Eder variants
    imposters.py       # open-set verification
    rolling.py         # within-text seam detection
    cluster.py         # exploratory only
  calibrate/
    controls.py        # positive (KJV) and negative (pseudo-biblical) harness
    null.py            # permutation / bootstrap baselines
    correction.py      # multiplicity handling
  claims/
    registry.py        # typed claims: evidence vs. required link
    conjunction.py     # chain modeling, joint probability
    accessibility.py   # pre-1830 availability gate
  report/
    schema.py          # versioned output contracts
    render.py
experiments/
  *.yaml               # pre-registered specifications
```

**The experiment specification is the load-bearing artifact.** It is written
*before* the run and is the unit of reproducibility and pre-registration:

```yaml
id: bom-internal-heterogeneity-001
hypothesis: >
  Holding register and quotation status constant, dictation-batch-1 material
  is stylometrically separable from dictation-batch-2 material.
corpus_version: "2026.08-a"
strata:
  hold_constant: [register: narrative, quotation: excluded]
  compare_across: composition.dictation_batch
features: cosine_delta_mfw_500
method: imposters_verification
controls:
  positive: kjv_book_boundaries
  negative: pseudobiblical_single_author
null_model: permutation_1000
multiplicity: {k: 1, correction: none}
falsifies_hypothesis_if: >
  separability does not exceed the negative-control false-split rate at
  the pre-declared threshold
```

Reject-if-missing: any of `strata`, `controls`, `null_model`,
`falsifies_hypothesis_if`.

---

## 3. Relationship to the existing toolkit

The current repo is a working prototype of roughly L0–L2, plus the L5 ledger:

| Layer | Existing | Gap |
|---|---|---|
| L0 | `corpus.verify_text_integrity`, OCR-tolerant matching | manifests, versioning, checksums |
| L1 | `segmenter.py` (structure + dictation batches, self-checking) | redaction, register, quotation, scribal stints |
| L2 | `stylometry.py` (function words, markers, richness) | char/POS n-grams, length standardization |
| L3 | cosine similarity, word n-gram reuse, `namesim.py` | Delta variants, imposters, rolling |
| L4 | `namesim` chance baselines; 71k-pair name base rate | control harness, permutation, correction |
| L5 | `parody_hypotheses.py`, `CONJUNCTION_AUDIT.md` | typed schema, automated chain math |
| L6 | `RESEARCH_LOG.md`, schema_version, 34 tests | pre-registration, adversarial pass |

The honest summary: the *discipline* is further along than the *methods*. The
chance-baseline instinct, the accessibility gate, and the evidence-vs-required-
link distinction are all built and load-bearing. The actual stylometry is still
cosine-on-word-frequencies, which is the weakest part of the stack.

---

## 4. What this contributes to the field

1. **A diagnosis of the disagreement.** The register confound explains why four
   competent studies reached four conclusions, without accusing anyone of bad
   faith.
2. **A measurement where there was a caveat.** KJV positive controls and
   pseudo-biblical negative controls turn "register might be confounding this"
   into a number.
3. **Open-set by default**, retiring the closed-set fallacy that consumed a
   decade of argument.
4. **Shared, versioned, integrity-checked corpora** — currently the field has no
   public code and no shared corpus at all ⏳, which is why nothing replicates.
5. **Pre-registration for a parallel-hunting field.** The apophenia problem is
   structural here, and the fix is procedural.
6. **A transmission-claim discipline** — accessibility gates, typed claims,
   conjunction math — that applies to the large non-stylometric portion of the
   literature.

---

## 5. Sequenced adoption

- **Phase 1 (foundation):** corpus manifests + integrity gates; migrate existing
  texts; acquire candidate-author corpora.
- **Phase 2 (stratification):** quotation masking first (largest contamination),
  then register tagging, then redaction layers.
- **Phase 3 (methods):** Cosine Delta, then imposters verification, validated
  against controls before any substantive run.
- **Phase 4 (calibration):** build the KJV and pseudo-biblical control harness.
  **No substantive authorship claim is made before this phase completes.**
- **Phase 5 (open science):** publish code, corpora manifests, and
  pre-registrations; invite adversarial replication.

The ordering is deliberate: calibration precedes claims. The field's recurring
failure has been to run the analysis first and discover the confound during peer
review.
