"""The shipped evaluation set must keep passing retrieval and refusal checks."""

from pathlib import Path

from ml.rag.evaluate import evaluate_cases, load_cases
from scheme_engine import SchemeEngine

DATASET = "data/schemes/schemes.json"
CASES = Path("ml/rag/eval_set.jsonl")


def test_eval_set_meets_thresholds():
    engine = SchemeEngine(DATASET)
    cases = load_cases(CASES)
    result = evaluate_cases(engine, cases)

    assert result["cases"] >= 10
    assert result["recall_at_3"] is not None and result["recall_at_3"] >= 0.90
    assert result["refusal_accuracy"] == 1.0
    assert result["citation_coverage"] == 1.0


def test_every_retrieved_scheme_has_a_dated_source():
    engine = SchemeEngine(DATASET)
    for case in load_cases(CASES):
        if case.get("expect_refusal"):
            continue
        result = engine.answer(case["query"])
        if not result["found"]:
            continue
        for citation in result["citations"]:
            assert citation["source_url"].startswith("http")
            assert citation["last_verified"]
            assert citation["review_due"]
