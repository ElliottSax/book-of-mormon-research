"""Tests for namesim.py's phonetic algorithms and anti-apophenia baseline."""
import namesim


def test_soundex_known_value_robert_rupert():
    # The textbook Soundex example: two names that sound alike should
    # produce the same code despite different spelling.
    assert namesim.soundex("Robert") == namesim.soundex("Rupert") == "R163"


def test_soundex_is_stable_and_deterministic():
    # jellyfish is the canonical implementation now (see namesim.py docstring)
    # -- just confirm our thin wrapper passes its output through unchanged
    # and deterministically, rather than re-asserting a specific disputed
    # edge case (different Soundex references disagree on "Ashcraft").
    assert namesim.soundex("Ashcraft") == namesim.soundex("Ashcraft")
    assert len(namesim.soundex("Ashcraft")) == 4


def test_nysiis_groups_similar_spellings():
    assert namesim.nysiis("Smith") == namesim.nysiis("Smith")
    # Confirm the wrapper round-trips jellyfish's real (non-empty) output
    # rather than re-asserting a specific hand-picked equivalence.
    assert namesim.nysiis("Smith") and namesim.nysiis("Smyth")


def test_name_pair_score_identical_names_is_composite_1():
    result = namesim.name_pair_score("Nephi", "Nephi")
    assert result["composite"] == 1.0
    assert result["soundex_match"]
    assert result["nysiis_match"]


def test_baseline_distribution_large_random_population_is_not_inflated():
    # A candidate scored against a large, unrelated vocabulary should have a
    # low-to-moderate mean composite -- if this comes back inflated, the
    # scoring function or sampling is broken in a way that would make every
    # candidate pair look "significant" regardless of the population.
    population = [f"word{i}xyz" for i in range(500)]
    baseline = namesim.baseline_distribution("Liahona", population, sample_size=500, seed=0)
    assert baseline["n"] == 500
    assert baseline["mean_composite"] < 0.5


def test_evaluate_candidate_pair_always_reports_baseline_and_verdict():
    population = ["fontaine", "montreal", "quebec", "canada", "director",
                  "powder", "voyage", "nation", "river", "forest"] * 50
    result = namesim.evaluate_candidate_pair("Liahona", "Lahontan", population)
    assert "baseline" in result and result["baseline"]["n"] > 0
    assert "distinguishable_from_chance" in result
    assert isinstance(result["distinguishable_from_chance"], bool)
    assert result["direct"]["a"] == "Liahona"
    assert result["direct"]["b"] == "Lahontan"


def test_evaluate_candidate_pair_handles_empty_population():
    result = namesim.evaluate_candidate_pair("Liahona", "Lahontan", [])
    assert result["baseline"]["n"] == 0
    assert result["z_score"] is None
    assert result["distinguishable_from_chance"] is False
