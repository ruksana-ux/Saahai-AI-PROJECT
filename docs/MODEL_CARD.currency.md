# Model card — Indian currency classifier

**Status: NOT TRAINED. This is the card the model must satisfy before release.**
Do not quote any number from this file until the corresponding row has a value
and a link to `benchmarks/results/`.

## Overview

| Field | Value |
|---|---|
| Model | MobileNetV3-Small (fallback: EfficientNet-Lite0) |
| Task | 13-class image classification |
| Classes | `unknown`, ₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000, ₹1 coin, ₹2 coin, ₹5 coin, ₹10 coin, ₹20 coin |
| Input | 224×224 RGB, float32, **raw 0–255** (no [0, 1] scaling) |
| Output | float32 **logits** over 13 classes; softmax applied on-device with the stored temperature |
| Runtime | TensorFlow Lite, int8 weights with float32 input/output, CPU (XNNPACK) |
| Size budget | ≤ 8 MB |
| Owner | Sahaaya Drishti ML |
| Last updated | 2026-11-18 (template) |

## Intended use

- A blind or low-vision user points the phone at a single note or coin.
- The app returns a denomination and a tactile verification cue.
- The app refuses when the top-1 probability is below 0.80 or the top-2 margin
  is below 0.15.
- A non-finite logit (NaN/Infinity) is rejected as `ModelError` and is never
  announced as a denomination.

## Out of scope

- Authentication or counterfeit detection.
- Counting a stack of notes or reading a denomination from a distance.
- Non-Indian currency.
- Identifying a note from a screenshot or a printed photo of a note.
- Any safety or navigation decision.

## Training data

See `docs/DATASET_CARD.currency.md`. Required before training:

- 500+ images per class, 13 classes, including a real `unknown` class.
- At least 10 background/device groups.
- Hard examples: crumple, partial occlusion, low light, glare, motion blur,
  angled view, note on patterned cloth.
- Split by background and device, not by frame.

## Evaluation

| Metric | Threshold | Measured | Date | Device |
|---|---|---|---|---|
| Top-1, clean | ≥ 0.97 | TBD | — | — |
| Top-1, hard | ≥ 0.90 | TBD | — | — |
| Top-2, hard | ≥ 0.97 | TBD | — | — |
| Unknown rejection AUROC | ≥ 0.95 | TBD | — | — |
| ECE after temperature scaling | ≤ 0.05 | TBD | — | — |
| p95 latency | ≤ 800 ms | TBD | — | — |
| Model size | ≤ 8 MB | TBD | — | — |

## Calibration

Temperature scaling is fitted on the validation set and the temperature is
stored in `currency_model.json`. The app uses the calibrated probabilities for
the threshold decision. If calibration is not applied, the card must say so.

## Failure modes to test explicitly

- A folded note showing only the blank half.
- Two notes overlapping.
- A note under a coloured light (auto-rickshaw interior, sodium street lamp).
- A coin on a similarly coloured floor.
- A screenshot of a note on another phone.
- A handwritten fake note.

## Ethical and accessibility notes

- The model must not be used to accuse anyone of passing a fake note.
- False negatives (saying "uncertain") are safer than false positives (naming
  the wrong denomination). Tune the threshold accordingly.
- Per-class recall is reported separately for coins and ₹2000, which are rare in
  everyday cash and easy to hide in an aggregate number.
- The model runs on-device; no image is retained or uploaded.

## Release checklist

- [ ] Dataset card complete with consent and licence
- [ ] Split verified by background/device
- [ ] Metrics table filled from `benchmarks/results/`
- [ ] Calibration applied and ECE reported
- [ ] Latency measured on the low-tier device
- [ ] Model hash recorded in the release notes
- [ ] Failure cases documented
