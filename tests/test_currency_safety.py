"""The currency engine must never invent a confidence score."""

import json
from pathlib import Path

import numpy as np
from PIL import Image

from currency_engine import CURRENCY_SPECS, DEFAULT_LABELS, SahaayaCurrencyEngine

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_missing_model_reports_model_unavailable_without_confidence():
    engine = SahaayaCurrencyEngine(
        model_path="definitely-not-a-real-model.tflite",
        meta_path="definitely-not-a-real-meta.json",
    )
    result = engine.classify_image(Image.new("RGB", (224, 224), "grey"))

    assert result["status"] == "model_unavailable"
    assert result["confidence"] is None
    assert result["denomination"] is None
    assert result["is_authenticity_check"] is False
    assert "cannot verify" in result["disclaimer"].lower()


def test_non_finite_model_output_is_a_model_error(monkeypatch):
    engine = SahaayaCurrencyEngine(
        model_path="definitely-not-a-real-model.tflite",
        meta_path="definitely-not-a-real-meta.json",
    )
    # Pretend a model loaded, then make it return a poisoned frame.
    engine.interpreter = object()
    monkeypatch.setattr(
        engine,
        "_predict",
        lambda _image: np.array([np.nan, 0.1, 0.2, 0.0], dtype=np.float32),
    )

    result = engine.classify_image(Image.new("RGB", (224, 224), "grey"))

    assert result["status"] == "model_error"
    assert result["confidence"] is None
    assert result["denomination"] is None
    assert result["is_authenticity_check"] is False


def test_rbi_bleed_line_counts():
    assert CURRENCY_SPECS["500"]["bleed_lines"] == 5
    assert CURRENCY_SPECS["200"]["bleed_lines"] == 4
    assert CURRENCY_SPECS["100"]["bleed_lines"] == 4
    # RBI lists bleed lines only from ₹100 upwards.
    assert CURRENCY_SPECS["50"]["bleed_lines"] == 0
    assert CURRENCY_SPECS["20"]["bleed_lines"] == 0
    assert CURRENCY_SPECS["10"]["bleed_lines"] == 0


def test_coin_twenty_is_twelve_sided():
    assert "12-sided" in CURRENCY_SPECS["coin_20"]["tactile_mark"]
    assert CURRENCY_SPECS["coin_20"]["kind"] == "coin"


def test_every_spec_has_a_kind_and_disclaimer_path():
    for key, spec in CURRENCY_SPECS.items():
        assert spec["kind"] in {"note", "coin"}, key
        assert spec["name"], key
        assert spec["tactile_mark"], key


def test_haptic_patterns_are_unique_per_denomination():
    patterns = {key: spec["haptic_pattern"] for key, spec in CURRENCY_SPECS.items()}
    assert len(set(patterns.values())) == len(patterns), patterns


def test_label_sources_agree():
    labels_txt = (REPO_ROOT / "ml" / "currency" / "labels.txt").read_text().split()
    android_labels = (
        REPO_ROOT / "android" / "app" / "src" / "main" / "assets" / "currency" / "labels.txt"
    ).read_text().split()
    classes = json.loads((REPO_ROOT / "data" / "currency" / "classes.json").read_text())
    class_keys = [item["key"] for item in classes["classes"]]

    assert labels_txt == DEFAULT_LABELS
    assert android_labels == DEFAULT_LABELS
    assert class_keys == DEFAULT_LABELS
    assert DEFAULT_LABELS[0] == "unknown"
    assert set(DEFAULT_LABELS[1:]) == set(CURRENCY_SPECS)
