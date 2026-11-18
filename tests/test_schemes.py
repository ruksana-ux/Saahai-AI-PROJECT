"""Scheme retrieval, citations and the eligibility rules engine."""

import json
import os

import pytest

from scheme_engine import Profile, SchemeEngine

DATASET = os.path.join("data", "schemes", "schemes.json")


@pytest.fixture(scope="module")
def engine() -> SchemeEngine:
    return SchemeEngine(DATASET)


def test_dataset_has_no_structural_errors(engine):
    assert engine.validation_errors() == []


def test_dataset_matches_json_schema(engine):
    jsonschema = pytest.importorskip("jsonschema")
    with open(DATASET, encoding="utf-8") as handle:
        data = json.load(handle)
    with open(os.path.join("data", "schemes", "schema.json"), encoding="utf-8") as handle:
        schema = json.load(handle)
    jsonschema.validate(instance=data, schema=schema)


def test_adip_income_slabs(engine):
    adip = engine.get("adip")
    assert adip is not None

    full = engine.evaluate_eligibility(
        adip, Profile(disability_percent=60, monthly_income_inr=20000, has_udid=True, has_aadhaar=True)
    )
    assert full["status"] == "eligible"
    assert full["subsidy_percent"] == 100

    half = engine.evaluate_eligibility(
        adip, Profile(disability_percent=60, monthly_income_inr=25000, has_udid=True, has_aadhaar=True)
    )
    assert half["status"] == "eligible"
    assert half["subsidy_percent"] == 50

    above = engine.evaluate_eligibility(
        adip, Profile(disability_percent=60, monthly_income_inr=40000, has_udid=True, has_aadhaar=True)
    )
    assert above["status"] == "not_eligible"


def test_adip_requires_40_percent_disability(engine):
    adip = engine.get("adip")
    result = engine.evaluate_eligibility(
        adip, Profile(disability_percent=30, monthly_income_inr=15000, has_udid=True, has_aadhaar=True)
    )
    assert result["status"] == "not_eligible"


def test_missing_profile_returns_unknown_not_eligible(engine):
    adip = engine.get("adip")
    result = engine.evaluate_eligibility(adip, None)
    assert result["status"] == "unknown"
    assert result["subsidy_percent"] is None


def test_answer_carries_source_and_verification_date(engine):
    result = engine.answer("What documents do I need for ADIP?")
    assert result["found"] is True
    assert "depwd.gov.in" in result["answer"]
    assert "Last verified" in result["answer"]
    assert result["citations"]
    assert result["citations"][0]["source_url"].startswith("http")


def test_answer_does_not_invent_unknown_schemes(engine):
    result = engine.answer("Is there a scheme for a free helicopter?")
    assert result["found"] is False
    assert result["citations"] == []
    assert "will not guess" in result["answer"].lower() or "could not find" in result["answer"].lower()


def test_udid_query_retrieves_udid(engine):
    result = engine.answer("How do I apply for a UDID card?")
    assert result["found"] is True
    assert result["matches"][0]["id"] == "udid"


def test_rpwd_reservation_query_retrieves_rpwd(engine):
    result = engine.answer("What reservation does RPwD give in government jobs and education?")
    assert result["found"] is True
    assert result["matches"][0]["id"] == "rpwd-act-2016"
