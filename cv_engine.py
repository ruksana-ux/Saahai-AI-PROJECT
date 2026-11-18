"""
Sahaaya AI - DEPRECATED street-scene prototype.

The original module claimed to detect potholes, open drains and low wires and
then told the user "Path clear" or "step 1 metre to the left". It used Sobel
edges and a dark-pixel ratio; it had no depth sensor, no trained detector, and
no field validation. Those statements were unsafe.

Street navigation is an explicit non-goal for Sahaaya Drishti v1. This module
is retained only so the old prototype still imports. It returns *visual cues*
with an explicit "not a mobility aid" status and never asserts that a path is
safe, never gives a distance in metres, and never gives a turn direction.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from PIL import Image

SAFETY_CLASS = "not_a_mobility_aid"

DISCLAIMER = (
    "This is a low-confidence visual cue from a single camera frame. It is not a "
    "mobility aid, it cannot detect drop-offs reliably, and it must not be used to "
    "decide whether it is safe to walk. Continue to use your white cane, guide dog "
    "or sighted assistance."
)


class SahaayaVisionEngine:
    """Deprecated scene-cue helper. Not safety-certified, not real-time."""

    def analyze_street_image(self, pil_image: Image.Image) -> Dict[str, Any]:
        image = np.asarray(pil_image.convert("RGB"), dtype=np.float32)
        height, width, _ = image.shape
        lower = image[int(height * 0.60) :, :, :]
        grey = lower.mean(axis=2)

        dark_ratio = float((grey < 45).mean())
        contrast = float(grey.std())

        cues: List[Dict[str, str]] = []
        if dark_ratio > 0.30:
            cues.append(
                {
                    "type": "dark_region",
                    "text": "A large dark region is visible in the lower part of the frame.",
                }
            )
        if contrast > 70:
            cues.append(
                {
                    "type": "high_contrast_region",
                    "text": "The lower part of the frame has strong light/dark contrast.",
                }
            )

        if not cues:
            cues.append(
                {
                    "type": "no_cue",
                    "text": (
                        "No strong visual cue was found. This does NOT mean the path "
                        "is clear."
                    ),
                }
            )

        return {
            "safety_class": SAFETY_CLASS,
            "disclaimer": DISCLAIMER,
            "cues": cues,
            "primary_status": "Visual cue only - not a mobility aid",
            "primary_action": (
                "Do not use this output to cross or walk. Use your cane or a human "
                "assistant."
            ),
            "is_danger": False,
            "confidence": None,
            "distance": None,
            "annotated_image": pil_image,
        }
