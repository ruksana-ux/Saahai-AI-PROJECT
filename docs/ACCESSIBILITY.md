# Accessibility requirements

The acceptance test is not "the screen looks fine". It is: **a blind user can
complete the task with TalkBack and no visual information.**

This file separates what is **implemented** from what is a **release target**. A
target is not evidence and must not be quoted as a measured result.

## TalkBack

Implemented:

- Every interactive control is a standard Android `Button`, `CheckBox`, `Switch`,
  `Spinner` or `EditText`, so TalkBack gets its name and role for free.
- Result fields use `android:accessibilityLiveRegion="polite"` and also set
  `contentDescription`, so a change is announced even when focus stays put.
- The camera preview and the guide box have `contentDescription`s that explain
  their purpose instead of being silent.
- Settings labels are tied to their controls with `android:labelFor`.
- Every result is also spoken by `SpeechEngine`, so the app never depends on
  TalkBack being enabled.
- No result is conveyed by colour, position or animation alone.

Target, not yet measured:

- Full manual focus-order review on a physical device.
- A recorded TalkBack pass on every screen.

## Touch and gesture

Implemented:

- Buttons use a 60 dp minimum height (`Widget.Sahaaya.Button`), above the 48 dp
  Android minimum.
- Primary actions sit at the bottom of each screen, above the tab bar.
- No multi-finger or timed gesture is required anywhere.
- Currency, document and scheme screens each have a **Repeat** / **Read again**
  control and a **Stop speaking** control.

Target:

- One-handed reachability test on small (5") and large (6.7") phones.

## Audio

Implemented:

- Long text is split at sentence boundaries. A single sentence longer than the
  speech chunk limit is split at a word boundary, never mid-word.
- Speech rate is adjustable from 0.5× to 2.0× and persists across launches.
- Nine Indian language tags are offered; if the device has no voice for the
  chosen language, `SpeechEngine` says which language it actually used.
- Speech stops when the app is paused, when a tab changes, and when the Stop
  button is pressed.

Target, not yet measured:

- Speech starts within 150 ms of the result being ready.
- Audio ducking during speech.
- Earcons for scanning, result and error. (There are haptic patterns instead.)

## Haptics

These are the patterns in `CurrencyCatalog.kt` (denominations) and
`HapticPatterns.kt` (generic cues), in milliseconds. Each denomination has a
distinct pattern, no generic cue reuses a denomination pattern, and unit tests
enforce both.

| Event | Pattern (ms) |
|---|---|
| Scan started | 40 once |
| Read/answer succeeded (document, scheme) | 80–50–80–50–80 |
| ₹10 note | 90 once |
| ₹20 note | 180 once |
| ₹50 note | 180–70–180 |
| ₹100 note | 180–70–180–70–180–70–180 (four long, fast gap) |
| ₹200 note | 180–120–180–120–180–120–180 (four long, slow gap) |
| ₹500 note | five long pulses, 70 ms gaps |
| ₹2000 note | seven long pulses, 70 ms gaps |
| ₹1 coin | 60 once |
| ₹2 coin | 120 once |
| ₹5 coin | 120–60–120 |
| ₹10 coin | 120–200–120 (long gap for the bimetallic ring) |
| ₹20 coin | 120–60–120–60–120 (three pulses for the 12-sided edge) |
| Uncertain | 250–80–250 |
| Error | 400–100–400–100–400 |

Haptics are a supplement, never the only channel: a phone can be on silent, in a
pocket, or have no vibrator. Every haptic event is paired with speech.

## Vision

Implemented:

- Light and dark colour sets with a contrast-checked body text colour.
- Text uses `sp`, so the system font scale applies.
- No information is conveyed only by red/green.

Target, not yet measured:

- Contrast ratio audit at 4.5:1 for body text and 3:1 for large text/controls.
- 200% font scale without clipping on every screen.
- A dedicated high-contrast theme. Only light and dark exist today.

## Cognitive

Implemented:

- One task per screen.
- The currency result uses a fixed order: denomination, tactile cue, disclaimer.
- Uncertain results name both candidates instead of picking one.
- Missing model, missing dataset and OCR failure each have a specific spoken
  message rather than a generic spinner.

Target:

- Error messages that say what to do next ("Move closer", "Tilt away from the
  light"). The current messages are honest but generic.

## Test protocol

Run this on a physical device before any release claim:

1. TalkBack on, screen curtain on, complete a currency scan.
2. TalkBack on, complete a document read in Latin and in Devanagari.
3. TalkBack on, ask a scheme question and reach the source URL.
4. Switch the system language to Hindi and repeat.
5. Increase font scale to 200% and repeat.
6. Enable "Remove animations" and repeat.
7. Test with a Bluetooth headset, with the phone speaker, and in silent mode.
8. Record task success, time on task, and the number of human interventions.

A release candidate fails if any core task needs a sighted helper.

## Known limitations in this build

- No voice input: there is no `SpeechRecognizer` and no microphone permission.
  Queries are typed, or chosen from preset buttons.
- The interface and the scheme dataset are English-only. The language setting
  selects the text-to-speech voice; it does not translate the UI or the answers.
- No screen-reader-only navigation mode; standard TalkBack traversal is used.
- Haptics cannot be felt through thick gloves or on devices without a vibrator.
