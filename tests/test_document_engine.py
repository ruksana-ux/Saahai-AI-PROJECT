"""Document OCR quality gate and honest failure modes."""

from PIL import Image

import document_engine


def test_blank_image_is_reported_as_low_quality():
    quality = document_engine.assess_quality(Image.new("RGB", (400, 400), "white"))
    assert quality["usable"] is False
    assert quality["issues"]


def test_missing_engines_returns_engine_unavailable(monkeypatch):
    monkeypatch.setattr(document_engine, "RAPIDOCR_AVAILABLE", False)
    monkeypatch.setattr(document_engine, "TESSERACT_AVAILABLE", False)

    result = document_engine.read_document(Image.new("RGB", (400, 400), "white"))
    assert result["status"] == "engine_unavailable"
    assert result["text"] == ""
    assert result["engine"] is None


def test_reading_order_uses_geometry_not_detection_order():
    blocks = [
        document_engine.TextBlock(text="second", confidence=0.9, x=10, y=100, width=50, height=20),
        document_engine.TextBlock(text="first", confidence=0.9, x=10, y=20, width=50, height=20),
        document_engine.TextBlock(text="same-line", confidence=0.9, x=80, y=22, width=60, height=20),
    ]
    ordered = document_engine._order_blocks(blocks)
    assert [block.text for block in ordered] == ["first", "same-line", "second"]


def test_join_blocks_inserts_paragraph_break_for_large_gap():
    blocks = [
        document_engine.TextBlock(text="Paragraph one.", confidence=0.9, x=10, y=10, width=100, height=20),
        document_engine.TextBlock(text="Paragraph two.", confidence=0.9, x=10, y=200, width=100, height=20),
    ]
    text = document_engine._join_blocks(blocks)
    assert "\n\n" in text
