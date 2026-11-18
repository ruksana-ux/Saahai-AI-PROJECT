"""Evaluate a currency model against the held-out split.

Accepts either a Keras model or an exported ``.tflite`` file::

    python ml/currency/evaluate.py \
        --model models/currency/currency_model.tflite \
        --data data/currency/dataset \
        --output benchmarks/results/currency_eval.json

The output contains the exact keys enforced by
``.github/workflows/ml-eval.yml``: ``top1_clean``, ``top1_hard``,
``top2_hard``, ``unknown_auroc`` and ``ece``.

"Hard" is taken from ``dataset/test_hard`` when that split exists. Otherwise it
is inferred from filename tags such as ``blur``, ``glare`` or ``crumple``. If
neither exists, hard metrics equal clean metrics and the JSON says so, so nobody
can mistake a clean-only run for a hard-set result.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import tensorflow as tf  # noqa: E402

from common import (  # noqa: E402
    TFLiteModel,
    compute_metrics,
    dataset_to_arrays,
    softmax_with_temperature,
)
from dataset import load_split, read_labels, write_json  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LABELS = Path(__file__).resolve().parent / "labels.txt"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}
HARD_TAGS = (
    "hard",
    "blur",
    "glare",
    "crumple",
    "crease",
    "fold",
    "lowlight",
    "low_light",
    "dark",
    "angle",
    "occl",
    "motion",
    "soiled",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=REPO_ROOT / "data" / "currency" / "dataset")
    parser.add_argument("--labels", type=Path, default=DEFAULT_LABELS)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "benchmarks" / "results" / "currency_eval.json")
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Calibration temperature. Defaults to the value stored beside the model.",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    return parser.parse_args()


def _class_paths(split_dir: Path, labels: Sequence[str]) -> List[Path]:
    paths: List[Path] = []
    for label in labels:
        class_dir = split_dir / label
        if not class_dir.is_dir():
            continue
        paths.extend(
            sorted(
                path
                for path in class_dir.iterdir()
                if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
            )
        )
    return paths


def _hard_mask(paths: Sequence[Path]) -> Optional[np.ndarray]:
    if not paths:
        return None
    mask = np.array(
        [any(tag in path.as_posix().lower() for tag in HARD_TAGS) for path in paths],
        dtype=bool,
    )
    return mask if mask.any() else None


def _read_temperature(model_path: Path, override: Optional[float]) -> float:
    if override is not None:
        return float(override)
    for candidate in (
        model_path.with_name("currency_model.json"),
        model_path.with_name("metrics.json"),
        model_path.parent / "metrics.json",
    ):
        if candidate.is_file():
            try:
                payload = json.loads(candidate.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if "temperature" in payload:
                return float(payload["temperature"])
    return 1.0


def _load_logits(model_path: Path, images: np.ndarray, batch_size: int) -> np.ndarray:
    if model_path.suffix.lower() == ".tflite":
        return TFLiteModel(str(model_path)).predict(images, batch_size=batch_size)
    model = tf.keras.models.load_model(model_path, compile=False)
    return np.asarray(model.predict(images, batch_size=batch_size, verbose=0), dtype=np.float32)


def _false_accept_rate(
    probabilities: np.ndarray, labels: np.ndarray, unknown_index: int, target_frr: float = 0.01
) -> Optional[float]:
    """FAR for the unknown class at a fixed false-reject rate.

    A false accept is a non-unknown image whose unknown score crosses the
    threshold. It is the dangerous error: the app names a denomination for
    something that is not a note.
    """
    scores = probabilities[:, unknown_index]
    is_unknown = labels == unknown_index
    if is_unknown.all() or not is_unknown.any():
        return None
    threshold = float(np.quantile(scores[is_unknown], target_frr))
    return float((scores[~is_unknown] >= threshold).mean())


def main() -> int:
    args = parse_args()
    labels = read_labels(args.labels)

    test_ds = load_split(
        args.data, "test", labels, batch_size=args.batch_size, shuffle=False
    )
    images, truth = dataset_to_arrays(test_ds)
    paths = _class_paths(args.data / "test", labels)
    if len(paths) != len(images):
        print(
            f"warning: reconstructed {len(paths)} paths for {len(images)} images; "
            "hard-set inference may be off",
            file=sys.stderr,
        )
        paths = []

    temperature = _read_temperature(args.model, args.temperature)
    logits = _load_logits(args.model, images, args.batch_size)
    probabilities = softmax_with_temperature(logits, temperature)

    hard_dir = args.data / "test_hard"
    hard_source = "none"
    if hard_dir.is_dir() and any(hard_dir.rglob("*")):
        hard_ds = load_split(
            args.data, "test_hard", labels, batch_size=args.batch_size, shuffle=False
        )
        hard_images, hard_truth = dataset_to_arrays(hard_ds)
        hard_probabilities = softmax_with_temperature(
            _load_logits(args.model, hard_images, args.batch_size), temperature
        )
        hard_metrics = compute_metrics(hard_probabilities, hard_truth, labels)
        hard_source = "test_hard split"
    else:
        mask = _hard_mask(paths)
        if mask is None:
            hard_metrics = compute_metrics(probabilities, truth, labels)
            hard_source = "clean test (no hard split or tags found)"
        else:
            hard_metrics = compute_metrics(probabilities, truth, labels, hard_mask=mask)
            hard_source = "filename tags in test split"

    clean_metrics = compute_metrics(probabilities, truth, labels)
    unknown_index = labels.index("unknown") if "unknown" in labels else None
    far = (
        _false_accept_rate(probabilities, truth, unknown_index)
        if unknown_index is not None
        else None
    )

    result = {
        "model": args.model.name,
        "model_sha256": _sha256(args.model),
        "temperature": temperature,
        "samples_clean": clean_metrics["samples"],
        "samples_hard": hard_metrics["samples"],
        "hard_source": hard_source,
        "top1_clean": clean_metrics["top1"],
        "top2_clean": clean_metrics["top2"],
        "top1_hard": hard_metrics["top1"],
        "top2_hard": hard_metrics["top2"],
        "unknown_auroc": hard_metrics["unknown_auroc"],
        "ece": clean_metrics["ece"],
        "ece_hard": hard_metrics["ece"],
        "false_accept_at_1pct_frr": far,
        "per_class_recall": clean_metrics["per_class_recall"],
        "confusion_matrix": clean_metrics["confusion_matrix"],
        "class_names": clean_metrics["class_names"],
    }

    write_json(args.output, result)
    print(json.dumps({key: result[key] for key in (
        "top1_clean", "top1_hard", "top2_hard", "unknown_auroc", "ece", "hard_source"
    )}, indent=2))
    print(f"wrote {args.output}")
    return 0


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
