# Claims matrix

Every user-facing claim must have one of: a test, a benchmark, a dated citation,
or an explicit "prototype" label. This file is the audit trail. Update it in the
same pull request as any claim change.

Status legend: **verified** (test/benchmark), **sourced** (dated official
citation), **prototype** (explicitly labelled, not a product claim),
**removed** (claim deleted), **pending** (not yet measured, must not be claimed).

| # | Claim | Previous state | Current evidence | Status | Enforced in |
|---|---|---|---|---|---|
| 1 | "100% pure Python" | In README and UI | Product client is Kotlin; ML training is Python | **removed** | `README.md`, `app.py` |
| 2 | "Offline neural RAG" | UI badge | Retrieval is TF-IDF/BM25; no neural encoder | **removed** | `rag_engine.py`, `app.py` |
| 3 | "9 Indian languages" | UI offered 9, AAC had 5, silent Hindi fallback | AAC now reports the fallback; UI states 5 AAC languages | **fixed** | `aac_engine.py`, `tests/test_aac_fallback.py` |
| 4 | "Counterfeit detection" | Checklist implied authentication | App states it cannot verify authenticity | **removed** | `currency_engine.py`, `app.py` |
| 5 | "Path clear" / "step 1 m left" | Street tab | Street navigation removed from v1; module returns "not a mobility aid" | **removed** | `cv_engine.py`, `docs/SAFETY.md` |
| 6 | "1.2 metres ahead" | Hard-coded distance | No distance output anywhere | **removed** | `cv_engine.py` |
| 7 | "SOS broadcast with GPS" | Hard-coded Delhi pin, no SMS/call | `tel:112` link; no automatic location | **removed** | `app.py` |
| 8 | "Haptic vibration pattern" in browser | Text only | Real haptics implemented on Android; browser says it is a demo | **prototype** | `android/.../HapticEngine.kt` |
| 9 | "Detected ₹500 (97% confidence)" | Confidence from mean pixel colour | Real TFLite model or `model_unavailable`; no invented score | **fixed** | `currency_engine.py`, `tests/test_currency_safety.py` |
| 10 | "Identifies coins" | Metadata only | Coins in class list and metadata; model not trained yet | **pending** | `data/currency/classes.json`, model card |
| 11 | "Real-time" | Streamlit still frames | Android pipeline is real-time by design; p95 not measured | **pending** | `docs/EVALUATION.md`, `benchmarks/` |
| 12 | "Works offline" | gTTS and cloud LLM in the path | Android core is on-device; prototype TTS needs network | **prototype** | `docs/ARCHITECTURE.md` |
| 13 | ADIP income limit ₹15,000 | Wrong 2024 limits | Official page: ₹22,500 / ₹22,501–₹30,000 | **sourced** | `data/schemes/schemes.json`, `tests/test_schemes.py` |
| 14 | Disability population "26.8M in 2026" | Mixed 2011 rate with 2026 population | 26.8M is the 2011 count; ~32.7M is a projection | **sourced** | `knowledge_base/demographics_data.json` |
| 15 | "Gemini 1.5 Flash active" | Retired model, deprecated SDK | Configurable current model via `google-genai` | **fixed** | `rag_engine.py` |
| 16 | "₹10/₹20/₹50 questions work" | Tokenizer dropped tokens ≤2 chars | Tokenizer keeps digits; regression test | **verified** | `tests/test_rag_tokenizer.py` |
| 17 | "Full answer read aloud" | 400-character truncation | Sentence chunking, 6000-character cap | **verified** | `tests/test_rag_tokenizer.py` |
| 18 | "Classroom quiz" | Showed correct answer before answering | Feedback only after Check | **fixed** | `app.py` |
| 19 | "ISL quiz" | Regenerated every rerun | Persisted in session state | **fixed** | `app.py` |
| 20 | "Preset question buttons" | Set state after widget creation | State set before widget creation | **fixed** | `app.py` |
| 21 | "XSRF/CORS protected" | Both disabled in config | Defaults restored | **fixed** | `.streamlit/config.toml` |
| 22 | "Token/cost" | None | N/A | — | — |
| 23 | "Live result never crashes the UI thread" | Analyzer delivered decisions on its background executor, then touched Views and TTS | Decisions are re-posted to the main looper before `onDecision` | **verified** | `CurrencyAnalyzer.kt` |
| 24 | "A broken model cannot name a note" | NaN/Inf logits passed every threshold comparison and rendered as a denomination | `ModelError` state in Kotlin and `model_error` status in Python; confidence is `None` | **verified** | `CurrencyGate.kt`, `currency_engine.py`, `tests/test_currency_safety.py`, `CurrencyGateTest.kt` |
| 25 | "One incidental word cannot trigger an answer" | A single shared token was enough to retrieve a scheme | Requires 2 distinct content tokens or an alias hit, in both engines | **verified** | `scheme_engine.py`, `SchemeEngine.kt`, `ml/rag/evaluate.py` |
| 26 | "Document lines are read in visual order" | Sorted by exact top edge, so a 1 px skew interleaved columns | 8 px row bucketing, then left-to-right | **verified** | `DocumentReader.kt` |
| 27 | "Haptics identify a denomination" | ₹100/₹200 and several coins shared identical patterns | Every label has a unique waveform; unit test enforces it | **verified** | `CurrencyCatalog.kt`, `CurrencyCatalogTest.kt`, `tests/test_currency_safety.py` |
| 28 | "Nothing leaves the device" | Manifest declared `INTERNET` and `ACCESS_NETWORK_STATE` with no network code | Permissions removed; app cannot open a socket | **verified** | `AndroidManifest.xml`, `docs/PRIVACY.md` |
| 29 | "Opening Settings does not load the model" | Settings instantiated TFLite just to show a status string | Asset-existence check only | **verified** | `CurrencyClassifier.isModelBundled`, `SettingsScreen.kt` |

## P0 defect log

| Defect | Root cause | Fix | Test |
|---|---|---|---|
| Clean clone crashes at startup | `st.secrets.get` raises `StreamlitSecretNotFoundError` when no secrets file exists | `secret()` catches the exception and falls back to env vars | manual import + CI smoke |
| Preset question does not appear in the input | `session_state` written after the widget was created | Presets are rendered before `text_input` | manual |
| Quiz shows correct answer immediately | Feedback rendered unconditionally | Feedback gated on a Check button | manual |
| ISL quiz changes on every interaction | `dict.get(key, generate())` evaluates the default every rerun | `if key not in session_state` initialisation | manual |
| Readout speed slider does nothing | Value never passed to TTS | `speed` passed to `text_to_speech_audio` | `tests/test_rag_tokenizer.py` |
| ₹10/₹20/₹50 queries lose the denomination | `len(token) > 2` filter | digits preserved | `tests/test_rag_tokenizer.py` |
| Long answers cut at 400 characters | `clean_text[:400]` | chunked synthesis | `tests/test_rag_tokenizer.py` |
| Currency confidence is fabricated | mean-colour heuristic | TFLite or `model_unavailable` | `tests/test_currency_safety.py` |
| SOS location is always Delhi | hard-coded coordinates | removed; `tel:112` only | manual |
| Haptics are text | no vibration API in Streamlit | Android `HapticEngine` | Android unit test |
| Silent language fallback | `get_translated_text` returned Hindi | explicit fallback metadata | `tests/test_aac_fallback.py` |
| ADIP limits wrong | stale 2024 draft | official 26.09.2024 revision | `tests/test_schemes.py` |
| Path-traversal static server | leftover `test-server.ps1` | deleted | repo scan |
| XSRF disabled | `enableXsrfProtection = false` | `true` | config review |
| UI updated from a background thread | Analyzer called `onDecision` inline on its executor | Decision re-posted to the main looper | `CurrencyAnalyzer.kt` |
| NaN confidence announced as a note | No finite check before threshold comparisons | `ModelError` / `model_error` path | `tests/test_currency_safety.py` |
| Single incidental token answered a scheme query | BM25 score alone gated the answer | ≥2 content tokens or alias hit | `ml/rag/evaluate.py` |
| Two denominations shared a haptic pattern | Patterns hand-written without a uniqueness check | Unique waveforms + test | `CurrencyCatalogTest.kt` |

## Rules for new claims

1. Do not write "real-time" without a p95 latency number from `benchmarks/`.
2. Do not write "offline" unless the feature was tested in airplane mode.
3. Do not write a percentage without the evaluation set and date.
4. Do not describe a rule-based answer as "AI-generated".
5. Do not describe a still-frame demo as a live camera assistant.
6. Do not add a language to the UI until every string in that flow exists.
