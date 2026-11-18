# Evaluation protocol

No number is published until it is produced by this protocol and stored in
`benchmarks/results/` with the date, device, model hash and dataset hash.

## Currency classification

### Metrics

| Metric | Why |
|---|---|
| Top-1 accuracy | Basic correctness |
| Top-2 accuracy | Supports the "I think X or Y" path |
| Unknown rejection AUROC | Can the model say "not currency"? |
| False-accept rate at 1% false-reject | Risk of naming the wrong note |
| Expected Calibration Error (ECE) | Does "90%" mean 90%? |
| p50 / p95 latency | Real-time claim |
| Model size | Low-end install budget |
| Per-class recall | Coins and ₹2000 are rare and easy to hide |

### Splits

- **Train / val / test** split by *background and device*, not by frame.
- At least 20% of test images from a device model not in training.
- A "hard" test set: low light, crumple, partial occlusion, motion blur, note on
  a patterned cloth, note held at an angle.
- The `unknown` class contains hands, tables, paper, other currencies, and
  screens — not random noise.

### Acceptance thresholds for a v1 release

| Metric | Threshold |
|---|---|
| Top-1 accuracy (clean) | ≥ 0.97 |
| Top-1 accuracy (hard) | ≥ 0.90 |
| Top-2 accuracy (hard) | ≥ 0.97 |
| Unknown rejection AUROC | ≥ 0.95 |
| ECE | ≤ 0.05 |
| p95 latency, 2 GB device | ≤ 800 ms |
| Model size (int8) | ≤ 8 MB |
| Per-class recall, coins | ≥ 0.90 |

If a threshold is missed, the feature ships as "beta" with the measured number
shown in the app, or it does not ship.

### Device matrix

| Tier | Example | RAM | Android |
|---|---|---|---|
| Low | Redmi 9A / Realme C series | 2–3 GB | 10 |
| Mid | Redmi Note 12 | 4–6 GB | 13 |
| High | Pixel 7 | 8 GB | 14 |

## OCR

| Metric | Definition |
|---|---|
| CER | Character error rate after normalisation |
| WER | Word error rate |
| Reading-order accuracy | Fraction of adjacent block pairs in correct order |
| Quality-gate precision | Share of rejected images that were genuinely unusable |
| p95 latency per A4 page | End to end |

Languages in this release: Latin and Devanagari script only, via the bundled ML
Kit recognisers. Other Indic scripts are out of scope until an offline recogniser
and a language-specific test set both exist; do not list them as supported.

## Scheme retrieval and rules

| Metric | Definition |
|---|---|
| Retrieval recall@3 | Correct scheme in the top 3 |
| Answer accuracy | Human-judged correct and complete |
| Citation accuracy | Cited URL actually supports the answer |
| Hallucination rate | Answers containing a fact absent from the dataset |
| Rules accuracy | Verdict matches a human-applied rule on 100 profiles |
| Refusal correctness | "Not found" on out-of-scope questions |

The evaluation set must include adversarial questions: a scheme that does not
exist, a state scheme not in the dataset, and an income exactly on a slab
boundary.

## Latency

Measure on device, release build, screen on, battery saver off, 10 runs after a
cold start. Report p50, p95 and worst case. "Real-time" requires p95 ≤ 2 s for a
currency scan and ≤ 3 s for a document page.

## Accessibility

Run the protocol in `docs/ACCESSIBILITY.md` with at least 20 participants,
including 10 blind TalkBack users. Report task success, time on task, and
interventions. A single participant failing a core task blocks release until
the cause is understood.
