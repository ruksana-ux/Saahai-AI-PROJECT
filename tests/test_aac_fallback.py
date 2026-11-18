"""AAC must announce a fallback instead of silently switching to Hindi."""

from aac_engine import SahaayaAACEngine


def test_kannada_is_supported():
    engine = SahaayaAACEngine()
    phrase = engine.get_phrases(engine.get_situations()[0])[0]
    result = engine.get_translation(phrase, "Kannada")
    assert result["supported"] is True
    assert result["fallback_from"] is None
    assert result["language_code"] == "kn"


def test_marathi_fallback_is_explicit():
    engine = SahaayaAACEngine()
    phrase = engine.get_phrases(engine.get_situations()[0])[0]
    result = engine.get_translation(phrase, "Marathi")
    assert result["supported"] is False
    assert result["fallback_from"] == "Marathi"
    assert result["language_code"] == "hi"
    assert result["text"]


def test_unknown_language_never_returns_empty_text():
    engine = SahaayaAACEngine()
    phrase = engine.get_phrases(engine.get_situations()[0])[0]
    result = engine.get_translation(phrase, "French")
    assert result["text"]
    assert result["supported"] is False
