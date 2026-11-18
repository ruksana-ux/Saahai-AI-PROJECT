# Architecture

## Principle

The critical path runs on the phone. Nothing in the currency, document or scheme
flow needs a network call, an account, or a server round trip. If the phone is in
airplane mode, every shipped feature still works with the bundled models and the
bundled scheme dataset.

This document describes **what the code does today**. Anything planned but not
built is marked *planned* and must not be described as working elsewhere.

```
┌──────────────────────────────────────────────────────────────┐
│ Android app (Kotlin, minSdk 26, targetSdk 35)                │
│                                                              │
│  MainActivity — one activity, four tabs, recreated on switch │
│                                                              │
│  Currency tab                          Document tab           │
│  ─────────────                         ────────────           │
│  CameraX Preview + ImageAnalysis       CameraX Preview +      │
│        │                               ImageCapture           │
│        ▼                                     │               │
│  rotate → centre crop (0.82)                 ▼               │
│        │                               manual capture button  │
│        ▼                                     │               │
│  CurrencyClassifier (TFLite, logits)         ▼               │
│        │                               ML Kit bundled Latin / │
│        ▼                               Devanagari recogniser   │
│  CurrencyGate → StabilityGate                │               │
│  (3 of last 4 frames agree)                  ▼               │
│        │                               reading-order sort     │
│        ▼                               (8 px row tolerance)   │
│  main-thread callback                        │               │
│        │                                     ▼               │
│        └──────────► SpeechEngine (TTS) + HapticEngine         │
│                                                              │
│  Schemes tab: bundled JSON → BM25 + eligibility rules →      │
│               answer with source URL + verification date     │
│                                                              │
│  Storage: SharedPreferences only. No Room. No history.        │
└──────────────────────────────────────────────────────────────┘
```

There is no backend in the critical path. `backend/` exists and is tested, but
the Android client does not call it in this release. When dataset refresh is
added it will be an explicit, user-initiated fetch that falls back to the
bundled asset.

## Why Android native

- CameraX gives a stable analysis stream and lifecycle handling.
- TFLite gives on-device inference without a network round trip.
- ML Kit's **bundled** text-recognition models work offline.
- Android TTS and `Vibrator` are first-class.
- TalkBack integration, content descriptions, live regions and focus order are
  controllable at the view level.
- Battery and thermal behaviour can be tuned (analysis resolution, frame rate).

A PWA cannot reliably drive haptics, cannot match CameraX's frame control, and
has weaker offline model support. Streamlit reruns the whole script on every
interaction and captures still frames; it is a demo, not a client.

## Module boundaries

All client code lives under
`android/app/src/main/java/org/sahaayadrishti/app/`.

| Package | Responsibility | Must not |
|---|---|---|
| `currency/` | Frames, stability gate, preprocess, infer, threshold, label | Claim authenticity |
| `document/` | Capture, recognise text, reconstruct reading order | Give legal advice |
| `schemes/` | Load dataset, retrieve, apply rules | Generate eligibility with an LLM |
| `speech/` | Queue utterances, language, completion | Truncate mid-sentence |
| `haptics/` | Named patterns per result | Be the only feedback channel |
| `settings/` | Local preferences, TalkBack shortcut | Upload anything |
| `util/` | Bitmap rotation/crop, safe `ImageProxy` decode | Hold state |

`MainActivity` owns `SpeechEngine`, `HapticEngine` and `SettingsStore` for the
life of the activity, so switching tabs does not restart the voice. Each tab
owns its camera binding and releases it when it is replaced.

## Data flow: currency scan

1. `ImageAnalysis` runs with `STRATEGY_KEEP_ONLY_LATEST` and `RGBA_8888` output
   on a single background executor.
2. At most one frame is processed at a time, and no more than one every 250 ms
   (~4 fps), so a cheap phone does not overheat.
3. The frame is rotated upright, then centre-cropped to `0.82` of the shorter
   side to match the on-screen guide box. It is resized to the model input and
   normalised per `currency_model.json` (`raw_0_255`).
4. The model returns logits over 13 classes, including `unknown`. Non-finite
   logits are rejected as `ModelError`; they are never treated as a confidence.
5. Decision policy (`CurrencyGate`):
   - non-finite score → `ModelError`;
   - `unknown` wins → `NotCurrency`;
   - top-1 < 0.80 or top-2 margin < 0.15 → `Uncertain` (names both candidates);
   - otherwise → `Identified` (denomination, tactile cue, haptic pattern).
6. `StabilityGate` releases a result only when 3 of the last 4 frames agree,
   then stays quiet for 2.5 s for the same label. A disagreement resets the run.
   `ModelError` uses its own internal label so a broken frame cannot be smoothed
   into a legitimate "not currency" result.
7. The decision is re-posted to the main looper before it touches Views or TTS.
8. If the model asset is absent, `CurrencyClassifier.create` fails, the scan
   button stays disabled, and the screen says the model is not installed. There
   is no heuristic fallback and no invented denomination.

## Data flow: document read

1. The user presses **Capture**. There is no auto-capture; a blind user needs a
   predictable moment, not a timer.
2. `ImageCapture` (minimise-latency mode) returns one frame. Rotation is read
   before the `ImageProxy` is closed, and the proxy is always closed.
3. The user-selected script picks the bundled ML Kit recogniser: Latin or
   Devanagari. Other Indic scripts are **not** supported in this release.
4. Lines from all blocks are sorted top-to-bottom with an 8 px row tolerance,
   then left-to-right, so multi-column pages are not interleaved.
5. A Laplacian-variance focus/contrast check runs on a downscaled copy. It does
   **not** reject the page, because re-shooting is hard without sight; it sets a
   quality warning that is spoken before the text.
6. The text is spoken sentence by sentence. It is also shown on screen for
   sighted helpers, and can be shared through the Android share sheet. Nothing
   is uploaded, saved to history, or written to disk.

## Data flow: scheme answer

1. The bundled `assets/schemes/schemes.json` is parsed at tab open. If it is
   missing or malformed, the tab says so and offers nothing else.
2. The query is normalised and tokenised; digits are preserved (`₹10`, `₹20`).
3. BM25 retrieves candidates. A result is refused unless it has at least two
   distinct matched content tokens or a scheme alias hit, so one incidental word
   cannot produce a confident wrong answer.
4. The rules engine evaluates the optional profile (disability %, monthly income,
   UDID, Aadhaar) against the dataset's declared thresholds.
5. The answer is assembled from dataset fields and always carries the official
   source URL and the date it was last verified. Records past `review_due` are
   shown with a stale warning.
6. There is no LLM in the Android client. Retrieval and eligibility are
   deterministic; the "AI" here is BM25 plus rules, not a generative model.

## Storage

- Scheme dataset: a read-only JSON asset inside the APK. There is no copy step,
  no Room database and no remote refresh in this release.
- Settings: `SharedPreferences` only — language tag, speech rate, haptics on/off,
  document script, and a telemetry opt-in flag that currently controls nothing
  because no telemetry client exists.
- History: none. Recognised text lives in memory until the tab is replaced.
- Camera frames: never written to disk.

## Failure modes

| Failure | Behaviour |
|---|---|
| Model file missing | Currency screen says "model not installed"; scan stays disabled; no guess |
| Model output NaN/Inf | `ModelError`; error haptic; "invalid result, try again" |
| Camera permission denied | Speaks why it is needed; scanning is unavailable |
| Camera bind fails | Speaks a generic error and an error haptic; scan stops |
| TTS engine missing or voice absent | `SpeechEngine` reports the language fallback; the result is still shown as text |
| OCR returns nothing | Says no text was found; uncertain haptic; nothing is invented |
| OCR throws | Generic error spoken; the bitmap is recycled in `finally` |
| Scheme dataset missing | Tab says the dataset was not found; no answer is fabricated |
| Scheme query is weak | "I could not find this"; no nearest-guess answer |
| Scheme record past `review_due` | Answer is shown with a stale warning and the review date |
| Backend unreachable | No effect: the client does not call the backend in this release |
