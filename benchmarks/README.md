# Benchmarks

**No results are published yet.** Every file in `results/` must be produced by a
real run on a real device or a real held-out split. A number without a device,
model hash, dataset hash and date is not a benchmark; it is a rumour.

## Result schema

`benchmarks/results/currency_eval.json` is written by
`ml/currency/evaluate.py`:

```json
{
  "model": "currency_model.tflite",
  "model_sha256": "...",
  "temperature": 1.42,
  "samples_clean": 1200,
  "samples_hard": 400,
  "hard_source": "test_hard split",
  "top1_clean": 0.0,
  "top2_clean": 0.0,
  "top1_hard": 0.0,
  "top2_hard": 0.0,
  "unknown_auroc": 0.0,
  "ece": 0.0,
  "ece_hard": 0.0,
  "false_accept_at_1pct_frr": 0.0,
  "per_class_recall": {},
  "confusion_matrix": [],
  "class_names": []
}
```

`benchmarks/results/latency_<device>.json` records on-device timing:

```json
{
  "device": "Redmi 9A",
  "ram_gb": 2,
  "android": "10",
  "build": "release",
  "runs": 50,
  "p50_ms": 0,
  "p95_ms": 0,
  "worst_ms": 0,
  "model_sha256": "...",
  "measured_at": "YYYY-MM-DD"
}
```

## Thresholds

See [`docs/EVALUATION.md`](../docs/EVALUATION.md). A missed threshold means the
feature ships as beta with the measured number shown in the app, or it does not
ship.

## Rules

- Report p50, p95 and worst case. "Real-time" is not a benchmark.
- Report per-class recall for coins and ₹2000 separately; they hide in an
  aggregate.
- Never paste a number from a validation split into a "test" field.
- Update [`docs/MODEL_CARD.currency.md`](../docs/MODEL_CARD.currency.md) in the
  same pull request.
