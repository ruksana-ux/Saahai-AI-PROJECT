# Competitors and positioning

This document is deliberately conservative. It records what other products do
and where the gap is; it does not claim we are better until we have measured it.

## Landscape

| Product | Strength | Gap Sahaaya Drishti targets |
|---|---|---|
| **RBI MANI** | Free, offline note identification from RBI | Notes only; explicitly not an authentication tool; no coins, documents or schemes |
| **Google Lookout / Seeing AI** | Strong general scene and OCR | Cloud-first or account-bound in several flows; English-first; not built around Indian currency, coins and scheme paperwork |
| **Kibo (Trestle Labs)** | Good document scanning and Indian-language support | Hardware-assisted or institutional workflow; cost and setup |
| **Be My Eyes** | Human help, high trust | Needs internet and a volunteer; not an offline tool |
| **SmartCane** | Ultrasonic obstacle detection | Hardware; above-ground obstacles; not money/documents/schemes |
| **Envision** | Strong general assistant | Subscription/cloud; not India-first |
| **NVDA / TalkBack** | Essential screen readers | They read the screen; they do not see the physical world |

## The wedge

These are v1 **targets**, not shipped results. Check the status table in
`README.md` before quoting any of them.

1. **Offline-first, on-device.** The core is designed to run in airplane mode.
2. **Indian currency *and* coins**, with an explicit unknown class.
3. **Latin and Devanagari documents**, in line order, not an OCR dump.
4. **Verified scheme navigator** with citations, dates and a rules engine.
5. **Uncertainty-aware feedback**: "I think ₹500 or ₹200; please rescan" instead
   of a fake 97%.
6. **Low-end device target**: Android 8+, 2 GB RAM, small install. The install
   size budget is not measured yet.
7. **Open benchmark, planned**: dataset card, model card, latency, failure cases.

## What we will not say

- "First" or "best" without a published benchmark.
- "Detects counterfeit notes."
- "Replaces a white cane."
- "Works in all nine languages" when only five have translations.
- "Real-time" before p95 latency is measured.

## What would falsify the positioning

- If a competitor ships an equally offline, equally accurate Indian
  currency+coin+document+scheme app on a 2 GB phone, the wedge narrows to
  execution and trust.
- If our model cannot reach the thresholds on low-end devices, the honest move
  is a narrower launch (documents and schemes first), not a louder claim.

Re-check this document every quarter and date the changes.
