# Dataset card — Indian currency images

**Status: collection not started.** This card defines what may be collected and
how it must be split. Do not publish accuracy numbers from a dataset that does
not follow it.

## Purpose

Train and evaluate an on-device classifier for Indian banknotes and coins for
blind and low-vision users.

## Classes

| Type | Classes |
|---|---|
| Notes | ₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000 |
| Coins | ₹1, ₹2, ₹5, ₹10, ₹20 |
| Negative | `unknown` (hands, tables, paper, other currencies, screens, blank wall) |

₹2000 is being withdrawn from circulation but remains legal tender; keep it in
the class list and note the date.

## Collection protocol

1. **Consent first.** Every participant signs a plain-language consent form in
   their language. The form states that images are used for a currency model,
   that faces are blurred, and that participation can be withdrawn.
2. **No faces.** Frame the note or coin only. If a face or identifying document
   is captured, blur it before upload.
3. **No serial numbers in the released set.** Crop or blur the serial number.
   Serial numbers are not needed for denomination classification and are
   personal data under DPDP.
4. **Device and background metadata.** Record device model, Android version,
   lighting condition, background type, and whether the note was crumpled.
5. **Ten background groups minimum.** Wooden table, steel plate, cloth, floor
   tile, concrete, paper, hand, shop counter, vehicle seat, outdoors.
6. **Hard examples are required, not optional.** At least 25% of each class must
   be crumpled, partially covered, angled, low-light or motion-blurred.
7. **Coins are photographed on three surfaces** (palm, floor, counter) and at
   two angles.

## Split

- Split by **background group and device**, never by random frame.
- Train 70%, validation 15%, test 15%.
- Hold out at least two device models and two background groups entirely.
- A "hard" test subset is reported separately.
- No image of the same physical note appears in both train and test.

## Annotation

- Label = denomination.
- Bounding box for the note or coin. Training crops to it; inference uses a
  fixed centre crop of 0.82 of the shorter side, matching the on-screen guide.
- Quality flags: blur, glare, occlusion, crumple.
- Two annotators for 10% of the set; disagreements resolved by a third.

## Privacy

- Faces, identity documents and serial numbers removed before upload.
- Images stored in a private bucket with access logging.
- Raw images deleted after the model is released, unless the participant
  explicitly consented to an open benchmark release.
- Open release, if any, contains only cropped notes/coins with no hands or
  backgrounds that identify a person.

## Known biases to measure

- New-series notes over-represented; older Mahatma Gandhi series under-represented.
- Bright indoor light over-represented; street and shop light under-represented.
- Notes are usually flat in photos; real notes are folded.
- Coins are small; a model can learn background instead of the coin. Test with
  the coin on unseen backgrounds.
- Regional circulation differences (₹2000 rarer in some states).

## Licence

- Model weights: to be decided before release.
- Dataset: not released until consent explicitly allows it.
- Code: MIT (see `LICENSE`).

## Versioning

Every dataset version records: date, image count per class, device list,
background list, annotation guide version, and a SHA-256 manifest.
