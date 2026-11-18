# Currency model assets

`CurrencyClassifier` looks for exactly two files here:

| File | Purpose |
| --- | --- |
| `currency_model.tflite` | int8 MobileNetV3-Small, float32 I/O, raw 0-255 input |
| `currency_model.json` | labels, input size, normalisation, temperature |

Both are produced by:

```bash
python ml/currency/train.py --data data/currency/dataset
python ml/currency/export_tflite.py --model artifacts/currency/model.keras
cp models/currency/currency_model.tflite android/app/src/main/assets/currency/
cp models/currency/currency_model.json   android/app/src/main/assets/currency/
```

`labels.txt` in this directory is the class order used by tests and by the
training script. The copy inside `currency_model.json` is authoritative at
runtime.

## What happens when the model is absent

The app **builds and runs**. The currency tab disables scanning, says a trained
model is not installed, and points to the tactile guide. It never falls back to
a colour heuristic or a hard-coded confidence. This is intentional: a wrong
denomination spoken with confidence is worse than an honest refusal.

`*.tflite` is gitignored. CI builds without a model and must keep passing.
