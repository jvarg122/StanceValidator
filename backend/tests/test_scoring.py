from app.credibility import score_source
from app.main import compute_overall_lean, compute_strength
from app.reuse import word_overlap


def test_strength_supported():
    evidence = [{"relation": "supports"}, {"relation": "supports"}]
    assert compute_strength(evidence) == "supported"


def test_strength_disputed():
    evidence = [{"relation": "conflicts"}, {"relation": "conflicts"}]
    assert compute_strength(evidence) == "disputed"


def test_strength_mixed():
    evidence = [{"relation": "supports"}, {"relation": "conflicts"}]
    assert compute_strength(evidence) == "mixed"


def test_strength_insufficient():
    assert compute_strength([]) == "insufficient evidence"


def test_overall_lean_well_supported():
    assert compute_overall_lean(["supported", "supported"]) == "well_supported"


def test_overall_lean_contested():
    assert compute_overall_lean(["supported", "disputed"]) == "contested"


def test_overall_lean_insufficient():
    assert compute_overall_lean(["insufficient evidence"]) == "insufficient_evidence"


def test_score_source_gov_is_high():
    assert score_source("https://www.eia.gov/report") == 0.9


def test_score_source_generic_is_low():
    assert score_source("https://example-blog.com/post") == 0.4


def test_word_overlap_identical():
    assert word_overlap("data centers use energy", "data centers use energy") == 1.0


def test_word_overlap_unrelated():
    assert word_overlap("data centers use energy", "cats are great pets") == 0.0
