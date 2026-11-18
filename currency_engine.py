"""
Sahaaya AI - Indian currency metadata and a real model loader.

This replaces the old colour heuristic that returned a hard-coded 91-97%
"confidence" from the mean pixel colour of the image. That was not a
classifier. Now:

  * if a trained TFLite model is present, it is used;
  * if no model is present, the result is ``model_unavailable`` and no
    confidence number is invented;
  * low-confidence predictions are reported as ``uncertain`` with a top-2 list;
  * a trained "unknown / not a note" class is required for rejection.

Tactile facts below were checked against RBI's "For Visually Impaired" page
(https://indiancurrency.rbi.org.in/visual-impairment) on 2026-11-18.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import numpy as np
from PIL import Image

try:  # optional at runtime; the prototype still runs without TensorFlow
    import tensorflow as tf

    TF_AVAILABLE = True
except Exception:  # noqa: BLE001 - TF can raise OSError on unsupported CPUs
    TF_AVAILABLE = False


DEFAULT_MODEL_PATH = os.getenv(
    "SAHAAYA_CURRENCY_MODEL", os.path.join("models", "currency", "currency_model.tflite")
)
DEFAULT_META_PATH = os.getenv(
    "SAHAAYA_CURRENCY_META", os.path.join("models", "currency", "currency_model.json")
)

#: Minimum top-1 probability before the app states a denomination.
CONFIDENCE_THRESHOLD = 0.80

#: If the top-2 margin is below this, ask the user to rescan.
MARGIN_THRESHOLD = 0.15


CURRENCY_SPECS: Dict[str, Dict[str, Any]] = {
    "2000": {
        "name": "₹2000 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Magenta",
        "motif": "Mangalyaan",
        "bleed_lines": 7,
        "tactile_mark": (
            "7 angular bleed lines and a raised horizontal rectangle with the "
            "denomination. RBI has announced withdrawal from circulation; the note "
            "remains legal tender."
        ),
        "haptic_pattern": "seven long pulses",
        "rbi_verified": True,
    },
    "500": {
        "name": "₹500 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Stone grey",
        "motif": "Red Fort",
        "bleed_lines": 5,
        "tactile_mark": (
            "5 angular bleed lines in three blocks on the left and right edges, "
            "plus a raised circle containing the denomination."
        ),
        "haptic_pattern": "five long pulses",
        "rbi_verified": True,
    },
    "200": {
        "name": "₹200 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Bright yellow",
        "motif": "Sanchi Stupa",
        "bleed_lines": 4,
        "tactile_mark": (
            "4 angular bleed lines with 2 circles in between, plus a raised "
            "'H' identification mark with microtext ₹200."
        ),
        "haptic_pattern": "four long pulses, slow",
        "rbi_verified": True,
    },
    "100": {
        "name": "₹100 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Lavender",
        "motif": "Rani ki Vav",
        "bleed_lines": 4,
        "tactile_mark": (
            "4 angular bleed lines, plus a raised triangular identification mark "
            "with microtext ₹100 above the Ashoka Pillar emblem."
        ),
        "haptic_pattern": "four long pulses, fast",
        "rbi_verified": True,
    },
    "50": {
        "name": "₹50 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Fluorescent blue",
        "motif": "Hampi with chariot",
        "bleed_lines": 0,
        "tactile_mark": (
            "No bleed lines on this denomination. Use the raised intaglio print, "
            "the note size, and the identification area above the Ashoka Pillar."
        ),
        "haptic_pattern": "two long pulses",
        "rbi_verified": True,
    },
    "20": {
        "name": "₹20 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Greenish yellow",
        "motif": "Ellora Caves",
        "bleed_lines": 0,
        "tactile_mark": (
            "No bleed lines on this denomination. Use the raised intaglio print "
            "and the note size."
        ),
        "haptic_pattern": "one long pulse",
        "rbi_verified": True,
    },
    "10": {
        "name": "₹10 Banknote",
        "kind": "note",
        "series": "Mahatma Gandhi (New) Series",
        "colour": "Chocolate brown",
        "motif": "Konark Sun Temple",
        "bleed_lines": 0,
        "tactile_mark": (
            "No bleed lines on this denomination. Use the raised intaglio print "
            "and the note size."
        ),
        "haptic_pattern": "one short pulse",
        "rbi_verified": True,
    },
    "coin_20": {
        "name": "₹20 Coin",
        "kind": "coin",
        "series": "Current circulation",
        "colour": "Silver / steel",
        "motif": "12-sided polygon",
        "bleed_lines": 0,
        "tactile_mark": (
            "12-sided (dodecagon) shape, designed so the edge can be counted by touch."
        ),
        "haptic_pattern": "three medium pulses",
        "rbi_verified": False,
    },
    "coin_10": {
        "name": "₹10 Coin",
        "kind": "coin",
        "series": "Current circulation",
        "colour": "Bimetallic",
        "motif": "Two-metal ring",
        "bleed_lines": 0,
        "tactile_mark": "Bimetallic: a distinct outer ring around an inner disc.",
        "haptic_pattern": "two medium pulses with a long gap",
        "rbi_verified": False,
    },
    "coin_5": {
        "name": "₹5 Coin",
        "kind": "coin",
        "series": "Current circulation",
        "colour": "Silver",
        "motif": "Round",
        "bleed_lines": 0,
        "tactile_mark": "Round and larger than the ₹2 coin; smooth raised rim.",
        "haptic_pattern": "two medium pulses",
        "rbi_verified": False,
    },
    "coin_2": {
        "name": "₹2 Coin",
        "kind": "coin",
        "series": "Current circulation",
        "colour": "Silver",
        "motif": "Round",
        "bleed_lines": 0,
        "tactile_mark": "Round, smaller than the ₹5 coin.",
        "haptic_pattern": "one medium pulse",
        "rbi_verified": False,
    },
    "coin_1": {
        "name": "₹1 Coin",
        "kind": "coin",
        "series": "Current circulation",
        "colour": "Silver",
        "motif": "Round",
        "bleed_lines": 0,
        "tactile_mark": "Round and the smallest of the commonly circulated coins.",
        "haptic_pattern": "one brief pulse",
        "rbi_verified": False,
    },
}

#: Label order must match the training output layer. See ml/currency/labels.txt.
DEFAULT_LABELS: List[str] = [
    "unknown",
    "10",
    "20",
    "50",
    "100",
    "200",
    "500",
    "2000",
    "coin_1",
    "coin_2",
    "coin_5",
    "coin_10",
    "coin_20",
]


class SahaayaCurrencyEngine:
    """Metadata lookup plus optional on-device TFLite inference."""

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH, meta_path: str = DEFAULT_META_PATH):
        self.model_path = model_path
        self.meta_path = meta_path
        self.labels = list(DEFAULT_LABELS)
        self.input_size = (224, 224)
        self.normalisation = "raw_0_255"
        self.temperature = 1.0
        self.output_is_logits = True
        self.interpreter = None
        self.model_error: Optional[str] = None
        self._load_model()

    # ------------------------------------------------------------------ model
    def _load_model(self) -> None:
        if not os.path.exists(self.model_path):
            self.model_error = (
                "No trained currency model is installed. The app will not guess a "
                "denomination."
            )
            return
        if not TF_AVAILABLE:
            self.model_error = "TensorFlow Lite runtime is not installed in this environment."
            return

        try:
            if os.path.exists(self.meta_path):
                with open(self.meta_path, "r", encoding="utf-8") as handle:
                    meta = json.load(handle)
                self.labels = meta.get("labels", self.labels)
                size = meta.get("input_size", list(self.input_size))
                self.input_size = (int(size[0]), int(size[1]))
                self.normalisation = meta.get("normalisation", "raw_0_255")
                self.temperature = float(meta.get("temperature", 1.0))
                self.output_is_logits = str(meta.get("output", "logits")).lower() != "softmax"

            self.interpreter = tf.lite.Interpreter(model_path=self.model_path)
            self.interpreter.allocate_tensors()
        except Exception as exc:  # noqa: BLE001
            self.interpreter = None
            self.model_error = f"Could not load the currency model: {exc}"

    @property
    def model_available(self) -> bool:
        return self.interpreter is not None

    def _preprocess(self, image: Image.Image) -> np.ndarray:
        """Resize and normalise exactly the way training did.

        ``raw_0_255`` is the default for the shipped model: MobileNetV3 is
        built with ``include_preprocessing=True``, so rescaling lives inside
        the TFLite graph. Dividing again here would double-scale the input and
        silently destroy accuracy.
        """
        resized = image.convert("RGB").resize(self.input_size, Image.BILINEAR)
        array = np.asarray(resized, dtype=np.float32)
        if self.normalisation == "raw_0_255":
            pass
        elif self.normalisation == "minus1_1":
            array = (array / 127.5) - 1.0
        elif self.normalisation == "0_1":
            array = array / 255.0
        else:
            raise ValueError(f"Unsupported normalisation: {self.normalisation}")
        return np.expand_dims(array, axis=0)

    def _predict(self, image: Image.Image) -> np.ndarray:
        assert self.interpreter is not None
        input_details = self.interpreter.get_input_details()
        output_details = self.interpreter.get_output_details()
        self.interpreter.set_tensor(input_details[0]["index"], self._preprocess(image))
        self.interpreter.invoke()
        output = np.asarray(
            self.interpreter.get_tensor(output_details[0]["index"])[0], dtype=np.float32
        )
        # The exported model returns logits. Temperature scaling is applied here
        # so the threshold decision uses calibrated probabilities.
        return self._to_probabilities(output)

    def _to_probabilities(self, output: np.ndarray) -> np.ndarray:
        if self.output_is_logits:
            scaled = output / max(self.temperature, 1e-3)
            scaled = scaled - scaled.max()
            exp = np.exp(scaled)
            return exp / exp.sum()
        if self.temperature and abs(self.temperature - 1.0) > 1e-6:
            # Already-softmaxed output: re-calibrate with the stored temperature.
            clipped = np.clip(output, 1e-12, 1.0)
            logits = np.log(clipped) / max(self.temperature, 1e-3)
            logits = logits - logits.max()
            exp = np.exp(logits)
            return exp / exp.sum()
        return output

    # --------------------------------------------------------------- classify
    def classify_image(self, pil_image: Image.Image) -> Dict[str, Any]:
        """Classify a note or coin, honestly.

        Returns a ``status`` of ``ok``, ``uncertain``, ``unknown``,
        ``model_error`` or ``model_unavailable``. Confidence is only reported
        when a model ran and returned finite numbers.
        """
        if not self.model_available:
            return {
                "status": "model_unavailable",
                "key": None,
                "denomination": None,
                "confidence": None,
                "top2": [],
                "message": self.model_error
                or "No currency model is installed in this build.",
                "is_authenticity_check": False,
                "disclaimer": (
                    "Identification aid only. This app cannot verify whether a note "
                    "is genuine."
                ),
            }

        probabilities = self._predict(pil_image)

        # A NaN/Inf logit survives every `< threshold` comparison, so the old
        # path would report "ok" with a NaN confidence. Refuse the frame.
        if not np.isfinite(probabilities).all():
            return {
                "status": "model_error",
                "key": None,
                "denomination": None,
                "confidence": None,
                "top2": [],
                "message": "The model returned an invalid score. Try again.",
                "is_authenticity_check": False,
                "disclaimer": (
                    "Identification aid only. This app cannot verify whether a note "
                    "is genuine."
                ),
            }

        order = np.argsort(probabilities)[::-1]
        top1_index = int(order[0])
        top1_key = self.labels[top1_index] if top1_index < len(self.labels) else "unknown"
        top1_probability = float(probabilities[top1_index])

        top2 = []
        for index in order[:2]:
            index = int(index)
            key = self.labels[index] if index < len(self.labels) else "unknown"
            top2.append({"key": key, "label": self._label(key), "probability": round(float(probabilities[index]), 4)})

        margin = float(probabilities[order[0]] - probabilities[order[1]]) if len(order) > 1 else 1.0

        if top1_key == "unknown":
            status = "unknown"
        elif top1_probability < CONFIDENCE_THRESHOLD or margin < MARGIN_THRESHOLD:
            status = "uncertain"
        else:
            status = "ok"

        spec = CURRENCY_SPECS.get(top1_key)
        return {
            "status": status,
            "key": top1_key,
            "denomination": spec["name"] if spec else "Not a recognised note or coin",
            "confidence": round(top1_probability, 4),
            "margin": round(margin, 4),
            "top2": top2,
            "spec": spec,
            "is_authenticity_check": False,
            "disclaimer": (
                "Identification aid only. This app cannot verify whether a note is "
                "genuine. Check the tactile marks or ask a bank."
            ),
        }

    @staticmethod
    def _label(key: str) -> str:
        spec = CURRENCY_SPECS.get(key)
        return spec["name"] if spec else "Not currency"

    def get_spec(self, key: str) -> Optional[Dict[str, Any]]:
        return CURRENCY_SPECS.get(key)
