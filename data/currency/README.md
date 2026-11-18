# Currency dataset

This directory holds **no images**. Images are large, personal, and may contain
faces or serial numbers, so they are never committed.

## Layout

```
data/currency/dataset/
  train/<class>/*.jpg
  val/<class>/*.jpg
  test/<class>/*.jpg
  test_hard/<class>/*.jpg   # optional, recommended
```

`<class>` must be one of the keys in [`classes.json`](classes.json) and must
match `ml/currency/labels.txt` exactly.

## Rules

1. Split by **background group and device**, never by random frame.
2. Hold out at least two device models and two background groups entirely.
3. No image of the same physical note in both train and test.
4. At least 25% of each class must be hard: crumpled, angled, low light, glare,
   motion blur, partially occluded.
5. The `unknown` class must contain hands, tables, paper, other currencies and
   screens — not random noise.
6. Blur faces and serial numbers before the image leaves the capture device.

The full protocol, consent language and privacy rules are in
[`docs/DATASET_CARD.currency.md`](../../docs/DATASET_CARD.currency.md).

## Quick validation

```bash
python ml/currency/train.py --data data/currency/dataset --epochs 1 --no-fine-tune
```

The script refuses to start if a split is missing, a class is empty, or a
filename appears in two splits.
