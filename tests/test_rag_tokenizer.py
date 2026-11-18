"""Regression tests for the P0 retrieval and speech bugs."""

from rag_engine import SahaayaRAGEngine


def make_engine() -> SahaayaRAGEngine:
    return SahaayaRAGEngine(kb_dir="knowledge_base")


def test_tokenizer_keeps_short_denominations():
    tokens = SahaayaRAGEngine.tokenize("How do I check a ₹10 note against ₹20 and ₹50?")
    assert "10" in tokens
    assert "20" in tokens
    assert "50" in tokens


def test_tokenizer_keeps_rupee_prefix_forms():
    tokens = SahaayaRAGEngine.tokenize("Rs. 500 and Rs 200 and 100/-")
    assert "500" in tokens
    assert "200" in tokens
    assert "100" in tokens


def test_retrieval_finds_adip_for_income_question():
    engine = make_engine()
    results = engine.retrieve("What is the ADIP income limit for a hearing aid?", top_k=3)
    assert results
    assert any("ADIP" in item["title"] or "ADIP" in item["content"] for item in results)


def test_unknown_question_returns_no_answer_instead_of_guessing():
    engine = make_engine()
    result = engine.generate_answer("What is the capital of Finland?")
    assert result["found"] is False
    assert result["citations"] == []


def test_speech_chunks_are_not_truncated_at_400_characters():
    engine = make_engine()
    text = " ".join(["This is a sentence about an assistive device."] * 40)
    chunks = engine._speech_chunks(text)
    assert len(" ".join(chunks)) > 400
    assert all(len(chunk) <= 180 for chunk in chunks)


def test_speech_chunks_remove_markdown_and_urls():
    chunks = SahaayaRAGEngine._speech_chunks(
        "**Important** see https://example.gov.in for details."
    )
    joined = " ".join(chunks)
    assert "**" not in joined
    assert "https://" not in joined
