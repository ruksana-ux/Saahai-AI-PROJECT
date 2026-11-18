"""Export the Keras model to an int8 TFLite file with float I/O.

Usage::

    python ml/currency/export_tflite.py \
        --model artifacts/currency/model.keras \
        --data data/currency/dataset \
        --output-dir models/currency

Why float input/output with int8 weights? The Android client hands raw 0-255
pixels to the interpreter and reads logits back. Keeping the boundary float
avoids a second copy of the quantisation maths in Kotlin, where a scale or
zero-point mistake would silently degrade accuracy.

If full int8 activation quantisation is unsupported for an op, the script falls
back to dynamic-range quantisation, records ``quantisation`` in the metadata and
prints a warning. It never pretends the smaller model is equivalent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402

from dataset import IMAGE_SIZE, read_labels, representative_dataset  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LABELS = Path(__file__).resolve().parent / "labels.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=REPO_ROOT / "data" / "currency" / "dataset")
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "models" / "currency")
    parser.add_argument("--samples", type=int, default=200)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument(
        "--no-int8",
        action="store_true",
        help="Export float32 weights (large; diagnostics only).",
    )
    return parser.parse_args()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _temperature(model_path: Path, override: float | None) -> float:
    if override is not None:
        return float(override)
    metrics = model_path.parent / "metrics.json"
    if metrics.is_file():
        try:
            return float(json.loads(metrics.read_text(encoding="utf-8"))["temperature"])
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            pass
    return 1.0


def _convert(model: tf.keras.Model, args: argparse.Namespace, labels: list[str]) -> tuple[bytes, str]:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    if args.no_int8:
        return converter.convert(), "float32"

    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.representative_dataset = lambda: representative_dataset(
        args.data, labels, samples=args.samples
    )
    converter.inference_input_type = tf.float32
    converter.inference_output_type = tf.float32

    try:
        converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
        return converter.convert(), "int8"
    except Exception as exc:  # noqa: BLE001 - converter raises many types
        print(f"int8 activation quantisation failed: {exc}", file=sys.stderr)
        print("falling back to dynamic-range quantisation", file=sys.stderr)
        fallback = tf.lite.TFLiteConverter.from_keras_model(model)
        fallback.optimizations = [tf.lite.Optimize.DEFAULT]
        return fallback.convert(), "dynamic_range"


def _verify(tflite_path: Path, model: tf.keras.Model, args: argparse.Namespace) -> float:
    """Compare TFLite top-1 against Keras on one real image. Returns agreement."""
    sample = next(
        iter(representative_dataset(args.data, read_labels(args.labels), samples=1)), None
    )
    if sample is None:
        return float("nan")

    batch = sample[0]
    keras_logits = np.asarray(model.predict(batch, verbose=0))[0]

    interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    interpreter.allocate_tensors()
    input_detail = interpreter.get_input_details()[0]
    output_detail = interpreter.get_output_details()[0]
    interpreter.set_tensor(input_detail["index"], batch.astype(np.float32))
    interpreter.invoke()
    tflite_logits = np.asarray(interpreter.get_tensor(output_detail["index"]))[0]

    return float(int(np.argmax(keras_logits) == np.argmax(tflite_logits)))


def main() -> int:
    args = parse_args()
    labels = read_labels(args.labels)
    model = tf.keras.models.load_model(args.model, compile=False)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    tflite_bytes, quantisation = _convert(model, args, labels)

    tflite_path = args.output_dir / "currency_model.tflite"
    tflite_path.write_bytes(tflite_bytes)
    (args.output_dir / "labels.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")

    agreement = _verify(tflite_path, model, args) if not args.no_int8 else 1.0

    meta = {
        "labels": labels,
        "input_size": [IMAGE_SIZE[0], IMAGE_SIZE[1]],
        "normalisation": "raw_0_255",
        "output": "logits",
        "temperature": _temperature(args.model, args.temperature),
        "quantisation": quantisation,
        "model_sha256": _sha256(tflite_path),
        "size_bytes": tflite_path.stat().st_size,
        "tflite_keras_top1_agreement": agreement,
        "exported_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "trained": True,
    }
    (args.output_dir / "currency_model.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )

    print(json.dumps(
        {
            "tflite": str(tflite_path),
            "size_mb": round(tflite_path.stat().st_size / 1e6, 2),
            "quantisation": quantisation,
            "temperature": meta["temperature"],
            "tflite_keras_top1_agreement": agreement,
        },
        indent=2,
    ))
    if agreement < 1.0:
        print("WARNING: TFLite and Keras disagree on the verification image.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
