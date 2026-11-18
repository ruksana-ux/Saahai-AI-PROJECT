"""Retrieval and refusal evaluation for the scheme navigator.

Usage::

    python ml/rag/evaluate.py --cases ml/rag/eval_set.jsonl --strict

Each JSONL line::

    {"query": "...", "expected_ids": ["adip"], "expect_refusal": false,
     "profile": {"disability_percent": 60, "monthly_income_inr": 20000,
                 "has_udid": true, "has_aadhaar": true}}

The harness reports recall@3, refusal correctness and citation coverage. It
exits non-zero under ``--strict`` when a threshold is missed, so CI can block a
regression instead of trusting a green badge.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scheme_engine import Profile, SchemeEngine  # noqa: E402

DEFAULT_CASES = Path(__file__).resolve().parent / "eval_set.jsonl"
DEFAULT_DATASET = REPO_ROOT / "data" / "schemes" / "schemes.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def load_cases(path: Path) -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
            if "query" not in case:
                raise ValueError(f"{path}:{number}: missing 'query'")
            cases.append(case)
    return cases


def _profile(case: Dict[str, Any]) -> Optional[Profile]:
    raw = case.get("profile")
    if not raw:
        return None
    return Profile(
        disability_percent=raw.get("disability_percent"),
        monthly_income_inr=raw.get("monthly_income_inr"),
        has_udid=raw.get("has_udid"),
        has_aadhaar=raw.get("has_aadhaar"),
        state=raw.get("state"),
    )


def evaluate_cases(engine: SchemeEngine, cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    details: List[Dict[str, Any]] = []
    recall_hits = 0
    retrieval_cases = 0
    refusals_correct = 0
    refusal_cases = 0
    citation_hits = 0
    citation_cases = 0

    for case in cases:
        result = engine.answer(case["query"], profile=_profile(case))
        expect_refusal = bool(case.get("expect_refusal", False))

        if expect_refusal:
            refusal_cases += 1
            ok = result["found"] is False
            refusals_correct += int(ok)
            details.append({"query": case["query"], "kind": "refusal", "ok": ok})
            continue

        retrieval_cases += 1
        expected = set(case.get("expected_ids", []))
        retrieved = [match["id"] for match in result.get("matches", [])[:3]]
        hit = bool(expected & set(retrieved))
        recall_hits += int(hit)

        if result.get("found"):
            citation_cases += 1
            citations = result.get("citations", [])
            cited = bool(citations) and all(
                str(item.get("source_url", "")).startswith("http") for item in citations
            )
            citation_hits += int(cited)
        else:
            cited = False

        details.append(
            {
                "query": case["query"],
                "kind": "retrieval",
                "expected": sorted(expected),
                "retrieved": retrieved,
                "ok": hit,
                "cited": cited,
            }
        )

    return {
        "cases": len(cases),
        "recall_at_3": (recall_hits / retrieval_cases) if retrieval_cases else None,
        "refusal_accuracy": (refusals_correct / refusal_cases) if refusal_cases else None,
        "citation_coverage": (citation_hits / citation_cases) if citation_cases else None,
        "details": details,
    }


def main() -> int:
    args = parse_args()
    engine = SchemeEngine(str(args.dataset))
    cases = load_cases(args.cases)
    result = evaluate_cases(engine, cases)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    summary = {key: result[key] for key in (
        "cases", "recall_at_3", "refusal_accuracy", "citation_coverage"
    )}
    print(json.dumps(summary, indent=2))

    failures = [item for item in result["details"] if not item.get("ok")]
    for item in failures:
        print(f"FAIL {item['kind']}: {item['query']}", file=sys.stderr)

    if not args.strict:
        return 0

    problems = []
    if (result["recall_at_3"] or 0) < 0.90:
        problems.append(f"recall@3 {result['recall_at_3']:.3f} < 0.90")
    if result["refusal_accuracy"] is not None and result["refusal_accuracy"] < 1.0:
        problems.append(f"refusal accuracy {result['refusal_accuracy']:.3f} < 1.0")
    if (result["citation_coverage"] or 0) < 1.0:
        problems.append(f"citation coverage {result['citation_coverage']:.3f} < 1.0")

    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
