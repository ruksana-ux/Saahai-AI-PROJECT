# Privacy

## Defaults

- Every shipped feature runs on the device: currency identification, document
  reading, and the scheme navigator.
- The app does not request the `INTERNET` permission in this release. There is no
  network client in the Android code, so "nothing is uploaded" is enforced by the
  operating system, not only by policy.
- No account, no sign-in, no advertising SDK, no analytics SDK.
- Camera frames are never written to disk and never leave the process.
- Recognised document text is held in memory only. There is no history and no
  saved transcript.
- The telemetry switch exists but is wired to nothing. It defaults to off and the
  settings screen says so in plain language.

## What leaves the device today

Nothing.

There is no dataset refresh, no crash reporter, no quality-metrics upload, no
cloud LLM, and no voice service. If a future release adds any of these, this
table must gain a row *in the same change*, and the permission must be added to
the manifest at the same time.

## What never leaves the device

- Camera frames and captured document images.
- Recognised document text.
- The scheme question and the eligibility profile (disability percentage, monthly
  income, UDID/Aadhaar yes-no answers).
- Contact list, SMS, call log, and precise location. The app requests none of
  these permissions.

## DPDP Act 2023 alignment

- **Consent**: no personal data is collected, so there is nothing to consent to.
  The reserved telemetry switch is separate from every other toggle and defaults
  to off.
- **Purpose limitation**: no data is processed for any secondary purpose.
- **Data minimisation**: the app holds only what the current screen needs.
- **Retention**: nothing is persisted except the user's own settings.
- **Correction and deletion**: settings can be changed or cleared through the
  Android app settings. There is no server-side record to delete.
- **Children**: no account, no ads, no profiling.

## Permissions

| Permission | Why | Required |
|---|---|---|
| `CAMERA` | Currency scanning and document capture | Yes, for those two features |
| `VIBRATE` | Haptic result cues | No, but harmless and non-personal |

No location, contacts, SMS, microphone, storage, internet or notification
permission is requested in this release.

## Threat model (short)

- **Shoulder surfing**: results are spoken aloud, so a nearby person can hear
  them. The app does not claim privacy from people in the same room. Audio
  routing follows the system (headset if the user has one connected).
- **Malicious dataset update**: not applicable yet — the scheme dataset is a
  read-only asset inside the signed APK, and there is no update channel.
- **Model tampering**: the TFLite model ships inside the signed APK; updates go
  through Play App Signing.
- **Log leakage**: debug builds log only generic failure messages. Release
  builds do not log recognised text, document text or predictions.
- **Backups**: `allowBackup="false"` and the backup rules exclude app data, so
  settings are not copied off the device by Android backup.
