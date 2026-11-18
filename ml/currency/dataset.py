"""Shared dataset utilities for the currency classifier.

Expected layout::

    data/currency/dataset/
      train/<class>/*.jpg
      val/<class>/*.jpg
      test/<class>/*.jpg

Class folder names must match ``labels.txt`` exactly. The split must be by
background and device, not by random frame. ``validate_split`` refuses to train
if the same filename appears in more than one split, which catches the most
common leak.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import tensorflow as tf

IMAGE_SIZE = (224, 224)
AUTOTUNE = tf.data.AUTOTUNE
SPLITS = ("train", "val", "test")


def read_labels(path: Path) -> List[str]:
    labels = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if "unknown" not in labels:
        raise ValueError("labels.txt must contain an 'unknown' class")
    if len(set(labels)) != len(labels):
        raise ValueError("labels.txt contains duplicates")
    return labels


def _files(directory: Path) -> List[Path]:
    return sorted(
        path
        for path in directory.rglob("*")
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
    )


def validate_split(dataset_dir: Path, labels: Sequence[str]) -> Dict[str, int]:
    """Check folders, class coverage and cross-split filename leakage."""
    counts: Dict[str, int] = {}
    seen: Dict[str, str] = {}
    problems: List[str] = []

    for split in SPLITS:
        split_dir = dataset_dir / split
        if not split_dir.is_dir():
            problems.append(f"missing split directory: {split_dir}")
            continue
        for label in labels:
            class_dir = split_dir / label
            if not class_dir.is_dir():
                problems.append(f"missing class directory: {class_dir}")
                continue
            files = _files(class_dir)
            counts[f"{split}/{label}"] = len(files)
            if not files:
                problems.append(f"empty class: {split}/{label}")
            for file in files:
                key = file.name.lower()
                if key in seen:
                    problems.append(
                        f"filename appears in two splits ({seen[key]} and {split}): {file.name}"
                    )
                seen[key] = split

    for split in ("train", "val"):
        for label in labels:
            key = f"{split}/{label}"
            if counts.get(key, 0) == 0:
                problems.append(f"class has no {split} images: {label}")

    if problems:
        raise ValueError("dataset validation failed:\n- " + "\n- ".join(problems))

    return counts


def load_split(
    dataset_dir: Path,
    split: str,
    labels: Sequence[str],
    batch_size: int = 32,
    shuffle: bool = False,
    seed: int = 1337,
) -> tf.data.Dataset:
    directory = dataset_dir / split
    dataset = tf.keras.utils.image_dataset_from_directory(
        directory,
        labels="inferred",
        label_mode="categorical",
        class_names=list(labels),
        image_size=IMAGE_SIZE,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=seed,
        interpolation="bilinear",
    )
    return dataset.prefetch(AUTOTUNE)


def augment(image: tf.Tensor, label: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
    """Augment before the model's own preprocessing.

    Keep brightness/contrast changes realistic: Indian notes are scanned under
    sodium lamps, tube lights, shade and phone flash.
    """
    image = tf.image.random_flip_left_right(image)
    image = tf.image.random_brightness(image, max_delta=0.18 * 255.0)
    image = tf.image.random_contrast(image, lower=0.75, upper=1.25)
    image = tf.image.random_saturation(image, lower=0.75, upper=1.25)
    image = tf.image.random_crop(image, size=(200, 200, 3))
    image = tf.image.resize(image, IMAGE_SIZE)
    return image, label


def apply_augmentation(dataset: tf.data.Dataset) -> tf.data.Dataset:
    return dataset.map(augment, num_parallel_calls=AUTOTUNE).prefetch(AUTOTUNE)


def class_weights(counts: Dict[str, int], labels: Sequence[str]) -> Dict[int, float]:
    totals = np.array([counts.get(f"train/{label}", 0) for label in labels], dtype=np.float64)
    present = totals > 0
    weights = np.zeros_like(totals)
    if present.any():
        weights[present] = totals[present].sum() / (present.sum() * totals[present])
    return {index: float(weight) for index, weight in enumerate(weights) if weight > 0}


def representative_dataset(
    dataset_dir: Path, labels: Sequence[str], samples: int = 200
) -> Iterable[List[np.ndarray]]:
    """Yield raw 0-255 float batches for int8 weight quantisation."""
    files: List[Path] = []
    per_class = max(1, samples // max(1, len(labels)))
    for label in labels:
        class_files = _files(dataset_dir / "train" / label)[:per_class]
        files.extend(class_files)

    def generator():
        for file in files:
            image = tf.keras.utils.load_img(file, target_size=IMAGE_SIZE)
            array = tf.keras.utils.img_to_array(image)
            yield [np.expand_dims(array, axis=0).astype(np.float32)]

    return generator()


def manifest_hash(dataset_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(dataset_dir.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(dataset_dir).as_posix().encode("utf-8"))
            digest.update(str(path.stat().st_size).encode("utf-8"))
    return digest.hexdigest()[:16]


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
