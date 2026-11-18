# Contributing

## Before you open a pull request

1. Read `docs/CLAIMS_MATRIX.md` and `docs/SAFETY.md`.
2. Run `pytest` and `ruff check .`.
3. If you changed a user-facing claim, update the claims matrix in the same PR.
4. If you changed the scheme dataset, update `last_verified`, `review_due` and
   `source_url`.
5. If you changed the Android UI, add a content description and test with
   TalkBack.

## Claims discipline

A PR that adds "real-time", "offline", a percentage, or a language must include
one of:

- a test that proves it,
- a benchmark result in `benchmarks/results/`,
- a dated official citation,
- or an explicit "prototype" label in the UI.

Reviewers should reject unsupported claims even if the code works.

## Safety-critical changes

Anything that tells a user how to move through space is out of scope for v1.
Do not add it in a PR. Open a design issue instead, with the sensor, validation
and fail-safe plan described in `docs/SAFETY.md`.

## Data changes

- Scheme records: official source URL, `last_verified` date, `review_due` date.
- Currency facts: cite RBI and date the check.
- Never commit participant images, faces, serial numbers or personal data.

## Code style

- Python: ruff, line length 100, type hints on public functions.
- Kotlin: official Kotlin style, no wildcard imports.
- Commit messages: imperative, scoped, e.g. `fix(currency): reject below threshold`.

## Tests

- Bug fix → regression test.
- New rule → table-driven test with boundary values.
- New language → test that the language actually exists and that fallback is
  announced.

## Accessibility review

Every UI PR answers:

- What does TalkBack say for each control?
- What is the focus order?
- Does the task work at 200% font scale?
- Is any information conveyed only by colour?
- Is there a non-audio fallback, and an audio fallback for visual output?

## Reporting a security issue

See `SECURITY.md`. Do not open a public issue for a vulnerability.
