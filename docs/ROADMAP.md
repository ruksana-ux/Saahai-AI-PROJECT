# Roadmap

Each milestone has an exit criterion. A milestone is not "done" because code was
written; it is done when the criterion is demonstrated.

## M0 — Truth pass (current)

- [x] Remove unsafe and unsupported claims from the prototype
- [x] Fix the P0 defects listed in `docs/CLAIMS_MATRIX.md`
- [x] Replace the currency colour heuristic with a real model loader
- [x] Add the citation-backed scheme dataset and rules engine
- [x] Add regression tests and CI
- [ ] Confirm GitHub push access and branch protection
- [ ] Archive the old README claims in the release notes

**Exit:** `pytest` passes; the prototype cannot state a denomination without a
model; every scheme answer has a source and a date.

## M1 — Currency (weeks 1–5)

- [ ] Collect 500+ images per class across 10 device/background groups
- [ ] Annotate note boundaries for the guide-box crop
- [ ] Train MobileNetV3-Small / EfficientNet-Lite0
- [ ] Temperature-scale and report ECE
- [ ] Export int8 TFLite; add to `android/app/src/main/assets/currency/`
- [ ] On-device latency benchmark on the low tier
- [ ] Publish model card and dataset card with real numbers

**Exit:** thresholds in `docs/EVALUATION.md` met on the hard test set, including
coins and unknown rejection.

## M2 — Documents (weeks 5–8)

- [x] ML Kit Latin + Devanagari pipeline (bundled, offline)
- [x] Reading-order reconstruction with row tolerance
- [ ] Paragraph breaks on top of line order
- [ ] Other Indic scripts — approach undecided; no Tesseract is bundled on Android
- [ ] Auto-capture quality gate (this release has manual capture plus a spoken quality warning)
- [ ] Sentence-level speech with a visual highlight (sentence speech exists; highlight does not)
- [ ] Save transcript (share exists; save does not)

**Exit:** a blind user reads a two-column form in logical order with TalkBack.

## M3 — Schemes (weeks 8–10)

- [ ] Expand the dataset to 25+ central and state schemes
- [ ] Add state-level rules and citations
- [ ] Add a review workflow with `review_due` alerts
- [ ] Evaluate retrieval and rules on 100 real questions
- [ ] Optional LLM paraphrase behind an explicit toggle

**Exit:** citation accuracy ≥ 95%, hallucination rate ≤ 1% on the evaluation set.

## M4 — Pilot (weeks 10–12)

- [ ] Recruit 20–30 blind/low-vision participants
- [ ] Run the accessibility protocol
- [ ] Fix the top five task failures
- [ ] Signed APK, privacy policy, changelog
- [ ] Publish the benchmark results

**Exit:** ≥ 80% task success without a sighted helper; no safety incident.

## Explicitly deferred

- street navigation and obstacle avoidance
- counterfeit detection
- deafblind communication
- ISL education
- AAC
- iOS client
- a universal "all disabilities" mode

## After v1

- offline voice input (Vosk) for scheme questions
- on-device Indic embeddings for retrieval
- document field extraction (name, date, amount)
- a public benchmark and dataset release with consent
