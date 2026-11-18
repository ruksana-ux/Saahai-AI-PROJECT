# Security policy

## Reporting

Email the maintainers privately or use GitHub's private vulnerability reporting.
Do not open a public issue for a vulnerability.

Include: affected version, steps to reproduce, impact, and any suggested fix.

## Scope

- Android app (`android/`)
- Python prototype (`app.py`, `*_engine.py`)
- Backend (`backend/`)
- Scheme dataset integrity

## High-priority classes

- A crafted image that causes the currency model to name the wrong denomination
  with high confidence.
- A dataset update that changes eligibility rules or source URLs without review.
- Path traversal or arbitrary file read in the prototype server.
- Secrets committed to the repository.
- Any code path that uploads an image or document without consent.

## Known and accepted in the prototype

- The Streamlit prototype is a demo. It is not hardened for public multi-tenant
  use. Do not deploy it with real user documents.
- gTTS sends the text to Google's servers. The prototype labels this; the
  Android client uses on-device TTS.
- The optional LLM receives the assembled scheme answer. It is off by default.

## Supported versions

Only the latest release and `main` receive fixes. The prototype is best-effort.

## Disclosure

We aim to acknowledge within 3 working days and to ship a fix or mitigation
within 30 days for high-severity issues.
