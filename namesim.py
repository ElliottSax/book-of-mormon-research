"""Name-derivation similarity toolkit, with a built-in null/baseline check.

Built for evaluating claimed wordplay/soundalike name-derivation hypotheses
(e.g. Lars Nielsen's claim that Book of Mormon names are "Kircherisms" --
playful derivations from 17th-century figures; the repo owner's own
Liahona/Lahontan hypothesis). These theories share a common methodological
risk: almost any two words share SOME phonetic or orthographic features by
chance, so a raw similarity score in isolation proves nothing. Every
evaluation here reports a candidate pair's score alongside a baseline
distribution of the same metric computed against a large random sample of
real words -- a score is only interesting if it sits well outside that
baseline.

This is a flagging heuristic, not a rigorous statistical hypothesis test.
Treat `distinguishable_from_chance` as "worth a closer, qualitative look",
not as proof of a real connection.

Phonetic codes (Soundex, NYSIIS, Metaphone) and Jaro-Winkler similarity come
from `jellyfish` (MIT, actively maintained, Rust-backed) rather than a
hand-rolled implementation -- an early version of this module hand-implemented
Soundex/NYSIIS, which is exactly the kind of subtle-bug risk a canonical,
widely-used library avoids. `difflib.SequenceMatcher` (stdlib) is kept as a
third, independent orthographic signal alongside jellyfish's Jaro-Winkler.
"""
from __future__ import annotations

import difflib
import re
from statistics import mean, pstdev
from typing import Iterable

import jellyfish


def _clean(word: str) -> str:
    return re.sub(r"[^A-Za-z]", "", word).upper()


def soundex(word: str) -> str:
    return jellyfish.soundex(_clean(word)) if _clean(word) else ""


def nysiis(word: str) -> str:
    return jellyfish.nysiis(_clean(word)) if _clean(word) else ""


def metaphone(word: str) -> str:
    return jellyfish.metaphone(_clean(word)) if _clean(word) else ""


def name_pair_score(a: str, b: str) -> dict:
    """Combine phonetic and orthographic similarity signals for one name
    pair into a single auditable record. `composite` is a simple documented
    blend, not a black box: 0.4 weight on continuous sequence-similarity
    (mean of SequenceMatcher ratio and Jaro-Winkler), 0.2 each for the three
    discrete phonetic-code matches (Soundex, NYSIIS, Metaphone).
    """
    ca, cb = _clean(a), _clean(b)
    sa, sb = soundex(a), soundex(b)
    na, nb = nysiis(a), nysiis(b)
    ma, mb = metaphone(a), metaphone(b)
    seq_ratio = difflib.SequenceMatcher(None, ca.lower(), cb.lower()).ratio()
    jaro_winkler = jellyfish.jaro_winkler_similarity(ca, cb) if ca and cb else 0.0
    soundex_match = bool(sa) and sa == sb
    nysiis_match = bool(na) and na == nb
    metaphone_match = bool(ma) and ma == mb
    composite = (
        0.4 * ((seq_ratio + jaro_winkler) / 2)
        + (0.2 * soundex_match) + (0.2 * nysiis_match) + (0.2 * metaphone_match)
    )
    return {
        "a": a,
        "b": b,
        "soundex_a": sa,
        "soundex_b": sb,
        "soundex_match": soundex_match,
        "nysiis_a": na,
        "nysiis_b": nb,
        "nysiis_match": nysiis_match,
        "metaphone_a": ma,
        "metaphone_b": mb,
        "metaphone_match": metaphone_match,
        "sequence_ratio": seq_ratio,
        "jaro_winkler": jaro_winkler,
        "composite": composite,
    }


def baseline_distribution(candidate: str, population: Iterable[str], sample_size: int = 2000, seed: int = 0) -> dict:
    """Score `candidate` against a large, fixed-seed sample of `population`
    (real vocabulary from a corpus, not an arbitrary dictionary) to
    establish what a "coincidental" composite score looks like for this
    candidate word specifically. Deterministic (fixed seed) so re-running
    produces the same baseline, not a moving target.
    """
    import random

    pool = [w for w in dict.fromkeys(population) if w]
    if not pool:
        return {"n": 0, "mean_composite": 0.0, "std_composite": 0.0, "max_composite": 0.0, "scores": []}
    rng = random.Random(seed)
    sample = pool if len(pool) <= sample_size else rng.sample(pool, sample_size)
    scores = [name_pair_score(candidate, w)["composite"] for w in sample]
    return {
        "n": len(scores),
        "mean_composite": mean(scores),
        "std_composite": pstdev(scores) if len(scores) > 1 else 0.0,
        "max_composite": max(scores),
    }


def evaluate_candidate_pair(name_a: str, name_b: str, baseline_population: Iterable[str],
                             z_threshold: float = 2.0) -> dict:
    """Top-level entry point: direct pair score plus a baseline computed by
    scoring name_a against a random sample of `baseline_population` (real
    vocabulary from the candidate-source corpus, e.g. via
    distinctive_name_population), and a z-score of the direct score against
    that baseline.

    `distinguishable_from_chance` is a documented-threshold flag (default
    z >= 2.0), not a rigorous hypothesis test -- this whole approach is
    vulnerable to the multiple-comparisons problem if many candidate pairs
    are tried and only the best-looking one is reported, so treat a True
    result here as "worth closer qualitative investigation", not proof.
    """
    direct = name_pair_score(name_a, name_b)
    baseline = baseline_distribution(name_a, baseline_population)
    std = baseline["std_composite"]
    z_score = (direct["composite"] - baseline["mean_composite"]) / std if std > 0 else None
    return {
        "name_a": name_a,
        "name_b": name_b,
        "direct": direct,
        "baseline": baseline,
        "z_score": z_score,
        "distinguishable_from_chance": bool(z_score is not None and z_score >= z_threshold),
        "z_threshold": z_threshold,
    }


def distinctive_name_population(text: str, min_len: int = 4) -> list[str]:
    """Build a baseline word population from a corpus's own distinctive
    proper nouns (reusing onomasticon_match's real-vocabulary extraction)
    rather than an arbitrary external dictionary, filtered to a minimum
    length so trivial short tokens don't dilute the baseline.
    """
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
    import onomasticon_match

    nouns = onomasticon_match.get_proper_nouns(text)
    return [w for w in nouns if len(w) >= min_len]
