# Sahaaya Drishti · सहाय दृष्टि

**An offline-first, on-device visual assistant for blind and low-vision users in India.**

This repository is the refactor of the original *Sahaaya AI* prototype. The
original Streamlit demo made claims the code did not support: "100% pure
Python", "offline neural", "9 languages", "counterfeit detection", "path clear",
"1.2 metres ahead", and a hard-coded Delhi SOS location. Those claims are being
removed, not decorated.

The production client is **Android native (Kotlin)**. The Streamlit app is kept
as a browser demo of the models and the scheme dataset.

---

## Status (honest)

| Area | State | Evidence |
|---|---|---|
| Legacy prototype bugs | Fixed; regression tests added (not yet executed here) | `tests/`, `docs/CLAIMS_MATRIX.md` |
| Scheme dataset | 4 records, sourced and dated | `data/schemes/schemes.json` |
| Scheme retrieval + rules | Working; regression tests added | `scheme_engine.py`, `tests/test_schemes.py` |
| Document OCR (Python) | Working when an OCR engine is installed | `document_engine.py` |
| Android client | Implemented; CI build defined but not yet run | `android/`, `.github/workflows/android-ci.yml` |
| Currency model | **Not trained yet** | `ml/currency/` pipeline + model card |
| On-device latency | **Not measured yet** | `benchmarks/` |
| User pilot | **Not run yet** | `docs/ROADMAP.md` |

The app deliberately says "no model installed" instead of inventing a
denomination. Do not ship it as a currency aid until the model card has real
numbers.

---

## What v1 does

1. **Identify Indian notes and coins** — ₹10 to ₹2000 notes and ₹1 to ₹20 coins,
   including the 12-sided ₹20 coin, with an explicit *unknown* class.
2. **Read printed documents aloud** — offline OCR, line-ordered text, and speech.
3. **Answer disability-scheme questions with citations** — ADIP, UDID, RPwD and
   Sugamya Bharat, with a rules-based eligibility check and a last-verified date.
4. **Open the dialler on 112** — from Settings, with 112 pre-filled. The app
   never places the call itself and never sends a location.

Everything above is designed to work in airplane mode on a low-end Android
phone. The Android client does not call the backend in this release; `backend/`
is a read-only dataset service for a future, user-initiated update path.

---

## What v1 does not do

- street navigation, pothole detection, or "path clear" announcements
- counterfeit detection
- distance estimates in metres
- deafblind communication, ISL education, or AAC (kept as out-of-scope prototypes)
- "all disabilities in one app"
- nine languages everywhere
- real-time video on the web client

See `docs/SAFETY.md` for why these are excluded.

---

## Repository layout

```
android/                 Kotlin client: CameraX, TFLite, ML Kit, TalkBack, haptics
ml/
  currency/              training, calibration, TFLite export, evaluation
  rag/                   retrieval evaluation harness
backend/                 FastAPI read-only dataset service
data/
  schemes/               versioned, citation-backed scheme dataset + JSON Schema
  currency/              class list and dataset collection protocol
benchmarks/              measured results only; empty until measured
docs/                    architecture, safety, claims matrix, model/dataset cards
tests/                   regression tests for the prototype and the new engines
legacy modules           app.py, rag_engine.py, currency_engine.py, ...
.github/workflows/       lint, tests, model eval, Android build, CodeQL
.devcontainer/           Codespaces environment with Python, Java and Android SDK
```

---

## Quick start: prototype (browser)

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
streamlit run app.py
```

The prototype works without any API key. If no OCR engine is installed it says
so; if no currency model is installed it says so.

Optional environment variables:

```bash
SAHAAYA_LLM_MODEL=gemini-2.0-flash
GEMINI_API_KEY=...
OPENAI_API_KEY=...
SAHAAYA_CURRENCY_MODEL=models/currency/currency_model.tflite
```

---

## Quick start: Android

Requirements: JDK 17, Android SDK 35, Gradle 8.9.

```bash
cd android
gradle :app:assembleDebug
```

Or open `android/` in Android Studio. In GitHub Codespaces the devcontainer
installs the SDK; run `scripts/setup-android-sdk.sh` once if it is missing.

The app needs `app/src/main/assets/currency/currency_model.tflite` to identify
currency. Without it, the currency screen states that the model is not installed.

---

## Train the currency model

```bash
pip install -r ml/requirements.txt
python ml/currency/train.py --data data/currency/dataset --epochs 20
python ml/currency/evaluate.py --model artifacts/currency/model.keras --data data/currency/dataset
python ml/currency/export_tflite.py --model artifacts/currency/model.keras
cp models/currency/currency_model.tflite android/app/src/main/assets/currency/
cp models/currency/currency_model.json   android/app/src/main/assets/currency/
```

Read `docs/DATASET_CARD.currency.md` before collecting images. The split must be
by background and device, not by random frame, or the reported accuracy is fake.
`evaluate.py` writes the exact keys `ml-eval.yml` enforces. Nothing is trained or
measured in this repository yet; `benchmarks/results/` is empty on purpose.

---

## GitHub workflow

- `python-ci.yml` — ruff, pytest, JSON schema validation
- `android-ci.yml` — Gradle build and Android lint
- `ml-eval.yml` — runs only when a model artifact exists; fails if metrics are missing
- `codeql.yml` — static analysis
- Issue templates require a reproduction and an accessibility impact statement
- `docs/CLAIMS_MATRIX.md` must be updated in the same PR as any user-facing claim

---

## Safety and privacy

- On-device by default. No image leaves the phone.
- No network permission is requested in this release.
- No account required for core features.
- No retention of camera frames.
- Emergency: the app opens the dialler on 112. It does not silently broadcast location.
- Currency: identification aid only, never authentication.
- Schemes: source URL and last-verified date on every answer.

Read `docs/SAFETY.md` and `docs/PRIVACY.md`.

---

## License

MIT. See `LICENSE`.
