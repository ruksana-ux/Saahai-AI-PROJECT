"""
Offline document OCR for the prototype.

The Android client uses the bundled ML Kit recognisers for Latin and Devanagari
only; other scripts are out of scope for this release. This module is the Python
equivalent used by the Streamlit prototype and by the OCR evaluation harness.

Engines, in order:
  1. RapidOCR (ONNX, pip-installable, models bundled, no network)
  2. Tesseract via pytesseract (needs the system binary)

If neither is installed the function returns ``engine_unavailable``. It never
invents text.

Reading order is reconstructed from bounding boxes instead of dumping raw OCR
lines in detection order, because a blind user cannot re-order a page visually.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
from PIL import Image, ImageFilter, ImageOps

try:
    from rapidocr_onnxruntime import RapidOCR

    RAPIDOCR_AVAILABLE = True
except Exception:  # noqa: BLE001 - import can fail on missing native libs
    RAPIDOCR_AVAILABLE = False

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except Exception:  # noqa: BLE001
    TESSERACT_AVAILABLE = False


@dataclass
class TextBlock:
    text: str
    confidence: float
    x: float
    y: float
    width: float
    height: float


def _laplacian_variance(grey: np.ndarray) -> float:
    """Focus measure. Higher is sharper."""
    if grey.shape[0] < 3 or grey.shape[1] < 3:
        return 0.0
    centre = grey[1:-1, 1:-1]
    neighbours = (
        grey[:-2, 1:-1]
        + grey[2:, 1:-1]
        + grey[1:-1, :-2]
        + grey[1:-1, 2:]
        - 4 * centre
    )
    return float(neighbours.var())


def assess_quality(image: Image.Image) -> Dict[str, Any]:
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    grey = rgb.mean(axis=2)
    blur_score = _laplacian_variance(grey)
    glare_ratio = float((grey > 245).mean())
    dark_ratio = float((grey < 25).mean())

    issues: List[str] = []
    if blur_score < 25:
        issues.append("The page looks blurry. Hold the phone still and try again.")
    if glare_ratio > 0.08:
        issues.append("There is glare on the page. Tilt the phone away from the light.")
    if dark_ratio > 0.45:
        issues.append("The page is too dark. Move to better light.")

    return {
        "blur_score": round(blur_score, 2),
        "glare_ratio": round(glare_ratio, 4),
        "dark_ratio": round(dark_ratio, 4),
        "issues": issues,
        "usable": not issues,
    }


def _prepare(image: Image.Image) -> Image.Image:
    prepared = ImageOps.exif_transpose(image).convert("RGB")
    if min(prepared.size) < 900:
        scale = 900 / min(prepared.size)
        prepared = prepared.resize(
            (int(prepared.width * scale), int(prepared.height * scale)), Image.LANCZOS
        )
    grey = ImageOps.autocontrast(prepared.convert("L"))
    grey = grey.filter(ImageFilter.SHARPEN)
    return grey


def _order_blocks(blocks: Sequence[TextBlock]) -> List[TextBlock]:
    if not blocks:
        return []

    heights = [block.height for block in blocks if block.height > 0]
    tolerance = (sum(heights) / len(heights) if heights else 12.0) * 0.6

    ordered = sorted(blocks, key=lambda block: (block.y, block.x))
    lines: List[List[TextBlock]] = []
    for block in ordered:
        placed = False
        for line in lines:
            line_centre = sum(item.y for item in line) / len(line)
            if abs(block.y - line_centre) <= tolerance:
                line.append(block)
                placed = True
                break
        if not placed:
            lines.append([block])

    lines.sort(key=lambda line: min(item.y for item in line))
    result: List[TextBlock] = []
    for line in lines:
        result.extend(sorted(line, key=lambda block: block.x))
    return result


def _join_blocks(blocks: Sequence[TextBlock]) -> str:
    """Join blocks into paragraphs using vertical gaps."""
    if not blocks:
        return ""

    output: List[str] = []
    previous: Optional[TextBlock] = None
    for block in blocks:
        text = block.text.strip()
        if not text:
            continue
        if previous is not None:
            gap = block.y - (previous.y + previous.height)
            if gap > max(previous.height, block.height) * 0.9:
                output.append("\n\n")
            elif gap > max(previous.height, block.height) * 0.25:
                output.append("\n")
            else:
                output.append(" ")
        output.append(text)
        previous = block

    joined = "".join(output)
    joined = re.sub(r"[ \t]+", " ", joined)
    joined = re.sub(r"\n{3,}", "\n\n", joined)
    return joined.strip()


def _rapidocr(image: Image.Image) -> Tuple[List[TextBlock], str]:
    engine = RapidOCR()
    array = np.asarray(image.convert("RGB"))
    raw = engine(array)
    result = raw[0] if isinstance(raw, tuple) else raw
    blocks: List[TextBlock] = []
    for item in result or []:
        try:
            box, text, confidence = item[0], item[1], item[2]
            xs = [point[0] for point in box]
            ys = [point[1] for point in box]
        except (TypeError, IndexError, ValueError):
            continue
        blocks.append(
            TextBlock(
                text=str(text),
                confidence=float(confidence),
                x=float(min(xs)),
                y=float(min(ys)),
                width=float(max(xs) - min(xs)),
                height=float(max(ys) - min(ys)),
            )
        )
    return blocks, "rapidocr-onnxruntime"


def _tesseract(image: Image.Image, lang: str) -> Tuple[List[TextBlock], str]:
    data = pytesseract.image_to_data(
        image, lang=lang, output_type=pytesseract.Output.DICT
    )
    blocks: List[TextBlock] = []
    for index, text in enumerate(data.get("text", [])):
        text = (text or "").strip()
        if not text:
            continue
        try:
            confidence = float(data["conf"][index])
        except (TypeError, ValueError):
            confidence = -1.0
        if confidence < 0:
            continue
        blocks.append(
            TextBlock(
                text=text,
                confidence=confidence / 100.0,
                x=float(data["left"][index]),
                y=float(data["top"][index]),
                width=float(data["width"][index]),
                height=float(data["height"][index]),
            )
        )
    return blocks, f"tesseract ({lang})"


def read_document(image: Image.Image, lang: str = "eng") -> Dict[str, Any]:
    """Read a document and return text in human reading order."""
    quality = assess_quality(image)
    prepared = _prepare(image)

    blocks: List[TextBlock] = []
    engine_name = ""
    errors: List[str] = []

    if RAPIDOCR_AVAILABLE:
        try:
            blocks, engine_name = _rapidocr(prepared)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"RapidOCR failed: {exc}")

    if not blocks and TESSERACT_AVAILABLE:
        try:
            blocks, engine_name = _tesseract(prepared, lang)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"Tesseract failed: {exc}")

    if not blocks and not RAPIDOCR_AVAILABLE and not TESSERACT_AVAILABLE:
        return {
            "status": "engine_unavailable",
            "text": "",
            "blocks": [],
            "engine": None,
            "quality": quality,
            "warning": (
                "No offline OCR engine is installed. Install rapidocr-onnxruntime "
                "or tesseract to use the document reader."
            ),
        }

    ordered = _order_blocks(blocks)
    text = _join_blocks(ordered)

    if not text:
        status = "no_text"
        warning = "No readable text was found. Move closer and fill the frame with the page."
    elif not quality["usable"]:
        status = "low_quality"
        warning = " ".join(quality["issues"]) + " The text below may contain errors."
    else:
        status = "ok"
        warning = ""

    return {
        "status": status,
        "text": text,
        "blocks": [
            {
                "text": block.text,
                "confidence": round(block.confidence, 3),
                "x": round(block.x, 1),
                "y": round(block.y, 1),
            }
            for block in ordered
        ],
        "engine": engine_name or None,
        "quality": quality,
        "warning": warning,
        "errors": errors,
    }
