"""Full analysis pipeline: runs every check this toolkit knows how to run
and writes a single consolidated reports/authorship_analysis.json.

Individual bookcli.py subcommands (compare/overlap/names/segment/namesim)
share these exact same underlying functions for one-off interactive queries
-- this script doesn't duplicate their logic, it just runs all of them.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

import stylometry
import corpus
import textreuse
import onomasticon_match
import segmenter
import namesim
import parody_hypotheses

# Bump this if the report's structure changes shape -- the previous
# integrate_brave_pipeline.py script silently read report keys
# (delta_distance, top_markers) that had never existed in this schema,
# producing an empty/wrong "successful" report. A version field gives any
# future consumer something to check instead of guessing.
SCHEMA_VERSION = 2


def run_analysis():
    texts = corpus.get_all_texts()
    results = {"schema_version": SCHEMA_VERSION}

    # 1. Pairwise stylometric comparison, including the Aeneid control text
    # (previously silently skipped -- corpus.get_all_texts() never loaded it).
    pairs = [
        ("book_of_mormon", "spalding_manuscript"),
        ("book_of_mormon", "lahontan_new_voyages"),
        ("book_of_mormon", "aeneid"),
    ]
    for name_a, name_b in pairs:
        results[f"{name_a}_vs_{name_b}"] = stylometry.compare_texts(
            name_a, texts[name_a], name_b, texts[name_b]
        )

    # 2. Onomasticon (proper-noun overlap) matching.
    results["onomasticon"] = onomasticon_match.match(
        texts["book_of_mormon"], texts["lahontan_new_voyages"]
    )

    # 3. Real structural segmentation (replaces the old hardcoded character-
    # offset slicing) -- per-book/chapter distribution of the Liahona-cluster
    # terms, plus the same broken out by dictation-order batch (Mosiah
    # priority: Mosiah-Moroni dictated first, 1 Nephi-Words of Mormon last).
    bom_raw = corpus.load_text(corpus.BOM_PATH)
    index = segmenter.build_index(bom_raw)
    results["liahona_term_segments"] = {}
    for term in sorted(stylometry.LIAHONA_TERMS):
        dist = segmenter.term_distribution(index, term)
        results["liahona_term_segments"][term] = {
            **dist,
            "by_dictation_batch": segmenter.by_dictation_batch(dist),
        }

    # 4. Word-level text-reuse detection (replaces the old naive character-
    # shingle approach) for both candidate-source pairs.
    results["textreuse_bom_vs_spalding"] = textreuse.reuse_report(
        "book_of_mormon", texts["book_of_mormon"],
        "spalding_manuscript", texts["spalding_manuscript"],
    )
    results["textreuse_bom_vs_lahontan"] = textreuse.reuse_report(
        "book_of_mormon", texts["book_of_mormon"],
        "lahontan_new_voyages", texts["lahontan_new_voyages"],
    )

    # 5. Name-derivation hypothesis registry, each evaluated with a
    # chance-baseline check against the relevant candidate-source vocabulary.
    results["parody_hypotheses"] = []
    for h in parody_hypotheses.HYPOTHESES:
        against_text = texts["lahontan_new_voyages"]
        population = namesim.distinctive_name_population(against_text)
        evaluation = namesim.evaluate_candidate_pair(h["name_a"], h["name_b"], population)
        results["parody_hypotheses"].append({
            "hypothesis_id": h["id"], "claim": h["claim"], "evaluation": evaluation,
        })

    Path("reports").mkdir(exist_ok=True)
    Path("reports/authorship_analysis.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Analysis complete. Results in reports/authorship_analysis.json")


if __name__ == "__main__":
    run_analysis()
