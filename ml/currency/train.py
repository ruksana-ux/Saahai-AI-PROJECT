"""Train the Indian currency classifier.

Usage (from the repository root)::

    python ml/currency/train.py \
        --data data/currency/dataset \
        --epochs 20 \
        --fine-tune-epochs 10 \
        --output-dir artifacts/currency

The script refuses to train if the dataset split is invalid (see
``dataset.validate_split``). That check exists because a random frame split
inflates accuracy by leaking the same physical note into train and test.

Outputs in ``--output-dir``:

    model.keras       fine-tuned Keras model (logits output, raw 0-255 input)
    metrics.json      validation metrics, temperature and dataset manifest hash
    history.json      per-epoch loss/accuracy
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make sibling modules importable when this file is run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import tensorflow as tf  # noqa: E402

from common import (  # noqa: E402
    build_model,
    collect_logits,
    compute_metrics,
    fit_temperature,
    softmax_with_temperature,
    unfreeze_top,
)
from dataset import (  # noqa: E402
    apply_augmentation,
    class_weights,
    load_split,
    manifest_hash,
    read_labels,
    validate_split,
    write_json,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA = REPO_ROOT / "data" / "currency" / "dataset"
DEFAULT_LABELS = Path(__file__).resolve().parent / "labels.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "artifacts" / "currency")
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--fine-tune-epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument(
        "--no-fine-tune",
        action="store_true",
        help="Train the classification head only (useful for a quick smoke run).",
    )
    parser.add_argument(
        "--no-augment",
        action="store_true",
        help="Disable augmentation (diagnostics only; do not ship a model trained this way).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tf.keras.utils.set_random_seed(args.seed)

    labels = read_labels(args.labels)
    counts = validate_split(args.data, labels)
    print(f"dataset OK: {len(labels)} classes, {sum(counts.values())} images")

    train_ds = load_split(
        args.data, "train", labels, batch_size=args.batch_size, shuffle=True, seed=args.seed
    )
    val_ds = load_split(args.data, "val", labels, batch_size=args.batch_size, shuffle=False)

    if not args.no_augment:
        train_ds = apply_augmentation(train_ds)

    model = build_model(len(labels))
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=4, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=2, min_lr=1e-6
        ),
    ]

    weights = class_weights(counts, labels)
    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        class_weight=weights or None,
        callbacks=callbacks,
    )

    if not args.no_fine_tune:
        model = unfreeze_top(model)
        fine_history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=args.fine_tune_epochs,
            class_weight=weights or None,
            callbacks=callbacks,
        )
        for key, values in fine_history.history.items():
            history.history.setdefault(key, []).extend(values)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.output_dir / "model.keras"
    model.save(model_path)

    val_logits, val_labels = collect_logits(model, val_ds)
    temperature, val_nll = fit_temperature(val_logits, val_labels)
    probabilities = softmax_with_temperature(val_logits, temperature)
    metrics = compute_metrics(probabilities, val_labels, labels)

    payload = {
        "split": "val",
        "temperature": temperature,
        "val_nll": val_nll,
        "dataset_manifest": manifest_hash(args.data),
        "class_counts": counts,
        "epochs": len(history.history.get("loss", [])),
        "fine_tuned": not args.no_fine_tune,
        "augmented": not args.no_augment,
        **metrics,
    }
    write_json(args.output_dir / "metrics.json", payload)
    write_json(args.output_dir / "history.json", history.history)

    print(json.dumps({k: payload[k] for k in ("top1", "top2", "ece", "temperature")}, indent=2))
    print(f"saved {model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
