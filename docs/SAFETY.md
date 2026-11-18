# Safety

Sahaaya Drishti is an information and identification aid. It is not a mobility
aid, a medical device, or an authentication device.

## Hard rules in code

| Rule | Implementation |
|---|---|
| Never say a path is clear | Street navigation removed from v1; `cv_engine.py` returns `not_a_mobility_aid` |
| Never estimate distance in metres | No distance field in any current result |
| Never claim counterfeit detection | `is_authenticity_check` is always `False`; disclaimer on every currency result |
| Never state a denomination below threshold | `CONFIDENCE_THRESHOLD = 0.80`, `MARGIN_THRESHOLD = 0.15`; otherwise `uncertain` with top-2 |
| Never invent a confidence score | If no model, `confidence = None` and `status = model_unavailable`; a non-finite score becomes `model_error` with no confidence |
| Never invent scheme eligibility | Rules engine in `scheme_engine.py`; dataset is the only source |
| Never hide a language fallback | `get_translation()` returns `fallback_from`; Android `SpeechEngine.onLanguageFallback` speaks the actual voice |
| Never broadcast location silently | Emergency is a `tel:112` link; no GPS read |

## Currency safety

- The app identifies a denomination; it does not authenticate a note.
- RBI's own MANI app states that it does not authenticate notes. We do not
  claim to do what RBI does not.
- Tactile guidance is quoted from RBI's "For Visually Impaired" page and dated
  in the UI. Coin descriptions are shape/size guidance, not authentication.
- If the model is uncertain, the user hears two candidates and is asked to
  rescan or use the tactile check.

## Document safety

- OCR output can be wrong. The app says so when the quality gate fails.
- Legal, medical and financial details must be verified with the issuing office.
- The app does not give medical advice or dosage instructions.

## Scheme safety

- Every answer includes the official source URL, the last-verified date and the
  review-due date.
- A record past `review_due` is shown with a stale warning.
- The Python prototype's language model, if configured, may only paraphrase
  retrieved text. It is never asked to decide eligibility. The Android client
  has no language model at all.
- "I could not find this" is a valid answer.

## Emergency

- `tel:112` is the only guaranteed action.
- The app does not send SMS, WhatsApp or a location pin automatically.
- A future opt-in SOS feature requires: explicit consent, a visible countdown,
  a cancel action, a test mode, and a privacy review. It is not in v1.

## What would make a feature safety-critical

Any feature that tells a blind user how to move through space needs:

1. a depth or range sensor, not a single RGB frame;
2. a trained detector with published failure rates;
3. a p95 end-to-end latency budget;
4. field validation with blind participants and orientation-and-mobility trainers;
5. a fail-safe behaviour when the model is uncertain;
6. a clear statement that the cane remains the primary aid.

Until all six exist, the feature stays out of the product.
