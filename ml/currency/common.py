"""Model construction, calibration and metrics shared by train/evaluate."""

from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

import numpy as np
import tensorflow as tf
from scipy.optimize import minimize_scalar
from sklearn.metrics import confusion_matrix, roc_auc_score

try:  # imported as ``ml.currency.common``
    from .dataset import IMAGE_SIZE
except ImportError:  # executed as a script from ``ml/currency``
    from dataset import IMAGE_SIZE


def build_model(num_classes: int, dropout: float = 0.2) -> tf.keras.Model:
    """MobileNetV3-Small with raw 0-255 input and logits output.

    ``include_preprocessing=True`` keeps the rescaling inside the model, so the
    TFLite file expects raw pixel values. That removes an entire class of
    train/serve skew.
    """
    base = tf.keras.applications.MobileNetV3Small(
        input_shape=(*IMAGE_SIZE, 3),
        include_top=False,
        weights="imagenet",
        include_preprocessing=True,
        minimalistic=False,
    )
    base.trainable = False

    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="image")
    features = base(inputs, training=False)
    pooled = tf.keras.layers.GlobalAveragePooling2D()(features)
    pooled = tf.keras.layers.Dropout(dropout)(pooled)
    logits = tf.keras.layers.Dense(num_classes, name="logits")(pooled)

    model = tf.keras.Model(inputs, logits, name="sahaaya_currency")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.CategoricalAccuracy(name="accuracy")],
    )
    return model


def unfreeze_top(model: tf.keras.Model, layers_from_end: int = 40, learning_rate: float = 1e-5) -> tf.keras.Model:
    backbone = next(layer for layer in model.layers if isinstance(layer, tf.keras.Model))
    backbone.trainable = True
    for layer in backbone.layers[:-layers_from_end]:
        layer.trainable = False
    # BatchNorm layers stay frozen during fine-tuning; small datasets break them.
    for layer in backbone.layers:
        if isinstance(layer, tf.keras.layers.BatchNormalization):
            layer.trainable = False

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.CategoricalAccuracy(name="accuracy")],
    )
    return model


def softmax_with_temperature(logits: np.ndarray, temperature: float) -> np.ndarray:
    temperature = max(float(temperature), 1e-3)
    scaled = logits / temperature
    scaled = scaled - scaled.max(axis=1, keepdims=True)
    exp = np.exp(scaled)
    return exp / exp.sum(axis=1, keepdims=True)


def _nll(temperature: float, logits: np.ndarray, labels: np.ndarray) -> float:
    probabilities = softmax_with_temperature(logits, temperature)
    picked = probabilities[np.arange(len(labels)), labels]
    return float(-np.log(np.clip(picked, 1e-12, 1.0)).mean())


def fit_temperature(logits: np.ndarray, labels: np.ndarray) -> Tuple[float, float]:
    """Return (temperature, validation NLL)."""
    result = minimize_scalar(
        lambda value: _nll(value, logits, labels),
        bounds=(0.05, 10.0),
        method="bounded",
    )
    return float(result.x), float(result.fun)


def expected_calibration_error(
    probabilities: np.ndarray, labels: np.ndarray, bins: int = 15
) -> float:
    confidence = probabilities.max(axis=1)
    predictions = probabilities.argmax(axis=1)
    correctness = (predictions == labels).astype(np.float64)

    edges = np.linspace(0.0, 1.0, bins + 1)
    error = 0.0
    for index in range(bins):
        lower, upper = edges[index], edges[index + 1]
        mask = (confidence > lower) & (confidence <= upper)
        if not mask.any():
            continue
        gap = abs(correctness[mask].mean() - confidence[mask].mean())
        error += gap * mask.mean()
    return float(error)


def compute_metrics(
    probabilities: np.ndarray,
    labels: np.ndarray,
    class_names: Sequence[str],
    hard_mask: np.ndarray | None = None,
) -> Dict[str, object]:
    predictions = probabilities.argmax(axis=1)
    top1 = float((predictions == labels).mean())

    top2_hits = 0
    for row, truth in zip(probabilities, labels, strict=True):
        top2_hits += int(truth in np.argsort(row)[-2:])
    top2 = top2_hits / len(labels)

    unknown_index = class_names.index("unknown") if "unknown" in class_names else None
    unknown_auroc = None
    if unknown_index is not None and len(set(labels)) > 1:
        is_unknown = (labels == unknown_index).astype(int)
        if 0 < is_unknown.sum() < len(is_unknown):
            unknown_auroc = float(roc_auc_score(is_unknown, probabilities[:, unknown_index]))

    matrix = confusion_matrix(labels, predictions, labels=list(range(len(class_names))))
    per_class = {}
    for index, name in enumerate(class_names):
        total = int(matrix[index].sum())
        per_class[name] = float(matrix[index, index] / total) if total else None

    result: Dict[str, object] = {
        "samples": int(len(labels)),
        "top1": top1,
        "top2": top2,
        "ece": expected_calibration_error(probabilities, labels),
        "unknown_auroc": unknown_auroc,
        "per_class_recall": per_class,
        "confusion_matrix": matrix.tolist(),
        "class_names": list(class_names),
    }

    if hard_mask is not None and hard_mask.any():
        result["top1_hard"] = float((predictions[hard_mask] == labels[hard_mask]).mean())
        hard_top2 = 0
        for row, truth in zip(probabilities[hard_mask], labels[hard_mask], strict=True):
            hard_top2 += int(truth in np.argsort(row)[-2:])
        result["top2_hard"] = hard_top2 / int(hard_mask.sum())
    else:
        result["top1_hard"] = result["top1"]
        result["top2_hard"] = result["top2"]

    # The workflow expects this exact key name.
    result["top1_clean"] = result["top1"]
    return result


def collect_logits(
    model: tf.keras.Model, dataset: tf.data.Dataset
) -> Tuple[np.ndarray, np.ndarray]:
    logits_batches: List[np.ndarray] = []
    label_batches: List[np.ndarray] = []
    for images, labels in dataset:
        logits_batches.append(model.predict(images, verbose=0))
        label_batches.append(np.argmax(labels.numpy(), axis=1))
    return np.concatenate(logits_batches), np.concatenate(label_batches)


class TFLiteModel:
    """TFLite wrapper that handles float and quantised input/output dtypes."""

    def __init__(self, path: str):
        self.interpreter = tf.lite.Interpreter(model_path=path)
        self.interpreter.allocate_tensors()
        self.input = self.interpreter.get_input_details()[0]
        self.output = self.interpreter.get_output_details()[0]

    def _prepare_input(self, image: np.ndarray) -> np.ndarray:
        dtype = self.input["dtype"]
        batch = np.expand_dims(image, axis=0)
        if dtype in (np.float32, np.float16):
            return batch.astype(dtype)
        scale, zero_point = self.input["quantization"]
        if not scale:
            raise ValueError(
                "Model expects an integer input but carries no quantisation "
                "parameters. Re-export with float input/output."
            )
        quantised = np.round(batch / scale + zero_point)
        info = np.iinfo(dtype)
        return np.clip(quantised, info.min, info.max).astype(dtype)

    def _read_output(self) -> np.ndarray:
        raw = self.interpreter.get_tensor(self.output["index"])[0]
        dtype = self.output["dtype"]
        if dtype in (np.float32, np.float16):
            return np.asarray(raw, dtype=np.float32)
        scale, zero_point = self.output["quantization"]
        if not scale:
            raise ValueError("Quantised output has no quantisation parameters.")
        return (raw.astype(np.float32) - zero_point) * scale

    def predict(self, images: np.ndarray, batch_size: int = 16) -> np.ndarray:
        outputs: List[np.ndarray] = []
        for start in range(0, len(images), batch_size):
            batch = images[start : start + batch_size]
            for image in batch:
                self.interpreter.set_tensor(self.input["index"], self._prepare_input(image))
                self.interpreter.invoke()
                outputs.append(self._read_output())
        return np.asarray(outputs)


def dataset_to_arrays(
    dataset: tf.data.Dataset,
) -> Tuple[np.ndarray, np.ndarray]:
    images: List[np.ndarray] = []
    labels: List[np.ndarray] = []
    for image_batch, label_batch in dataset:
        images.append(image_batch.numpy())
        labels.append(np.argmax(label_batch.numpy(), axis=1))
    return np.concatenate(images), np.concatenate(labels)
