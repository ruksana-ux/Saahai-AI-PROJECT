"""
Citation-backed scheme retrieval and eligibility rules.

Design rules
------------
1. The dataset (``data/schemes/schemes.json``) is the only source of truth.
2. Every answer carries the official source URL and the last-verified date.
3. Eligibility is computed by rules, never by a language model.
4. If retrieval is weak, the engine says it does not know.
5. If a record is past ``review_due``, it is still shown but marked stale.
"""

from __future__ import annotations

import json
import math
import os
import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_DATASET = os.path.join("data", "schemes", "schemes.json")

#: Below this BM25 score the engine refuses to answer.
MIN_SCORE = 1.0

STOPWORDS = {
    "a", "about", "also", "an", "and", "any", "are", "as", "at", "be", "by", "can", "do",
    "does", "exactly", "for", "from", "get", "give", "how", "i", "if", "in", "into", "is",
    "it", "its", "me", "much", "my", "no", "not", "of", "on", "or", "per", "please", "some",
    "that", "the", "there", "these", "this", "those", "to", "under", "what", "when", "where",
    "which", "who", "will", "with", "you",
}

#: Words that appear in almost every scheme record. A query made only of these
#: must not retrieve a specific scheme; otherwise "is there a free helicopter
#: scheme?" returns ADIP just because the word "scheme" occurs there.
GENERIC_TOKENS = {
    "scheme", "schemes", "yojana", "government", "govt", "india", "indian",
    "disability", "disabilities", "disabled", "person", "persons", "people",
    "benefit", "benefits", "apply", "application", "document", "documents",
    "information", "details", "tell", "about", "help", "support", "available",
    "eligibility", "eligible", "need", "needs", "required", "requirement",
}


def tokenize(text: str) -> List[str]:
    lowered = text.lower().replace("₹", " ").replace("rs.", " ").replace("rs", " ")
    lowered = re.sub(r"[^\w\s/%-]", " ", lowered)
    tokens: List[str] = []
    for raw in lowered.split():
        token = raw.strip("/")
        if not token or token in STOPWORDS:
            continue
        if len(token) == 1 and not token.isdigit():
            continue
        tokens.append(token)
    return tokens


@dataclass(frozen=True)
class Profile:
    """Optional user facts used by the rules engine."""

    disability_percent: Optional[float] = None
    monthly_income_inr: Optional[float] = None
    has_udid: Optional[bool] = None
    has_aadhaar: Optional[bool] = None
    state: Optional[str] = None


@dataclass
class ScoredScheme:
    scheme: Dict[str, Any]
    score: float


class SchemeEngine:
    def __init__(self, dataset_path: str = DEFAULT_DATASET):
        self.dataset_path = dataset_path
        self.dataset: Dict[str, Any] = {}
        self.schemes: List[Dict[str, Any]] = []
        self._index: Dict[str, Dict[str, Any]] = {}
        self._doc_tokens: List[List[str]] = []
        self._avg_len = 0.0
        self.load()

    # ------------------------------------------------------------------- load
    def load(self) -> None:
        with open(self.dataset_path, encoding="utf-8") as handle:
            self.dataset = json.load(handle)
        self.schemes = list(self.dataset.get("schemes", []))
        self._build_index()

    def _document_text(self, scheme: Dict[str, Any]) -> str:
        parts: Iterable[str] = [
            scheme.get("name", ""),
            " ".join(scheme.get("aliases", [])),
            scheme.get("category", ""),
            scheme.get("summary", ""),
            " ".join(scheme.get("benefits", [])),
            " ".join(scheme.get("documents_required", [])),
            " ".join(scheme.get("how_to_apply", [])),
            " ".join(scheme.get("eligibility", {}).get("notes", [])),
        ]
        return " ".join(parts)

    def _build_index(self) -> None:
        documents = [tokenize(self._document_text(scheme)) for scheme in self.schemes]
        self._doc_tokens = documents
        document_count = len(documents) or 1
        self._avg_len = sum(len(doc) for doc in documents) / document_count if documents else 0.0

        frequencies: Dict[str, int] = {}
        for doc in documents:
            for token in set(doc):
                frequencies[token] = frequencies.get(token, 0) + 1

        self._index = {}
        for token, df in frequencies.items():
            self._index[token] = {
                "df": df,
                "idf": math.log(1 + (document_count - df + 0.5) / (df + 0.5)),
            }

    # -------------------------------------------------------------- retrieval
    def search(self, query: str, top_k: int = 3) -> List[ScoredScheme]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # A query built only from generic words cannot identify a scheme.
        informative = [
            token
            for token in query_tokens
            if token not in GENERIC_TOKENS and token in self._index
        ]
        if not informative:
            return []

        k1, b = 1.5, 0.75
        scored: List[ScoredScheme] = []
        for scheme, tokens in zip(self.schemes, self._doc_tokens, strict=True):
            length = len(tokens) or 1
            counts: Dict[str, int] = {}
            for token in tokens:
                counts[token] = counts.get(token, 0) + 1

            score = 0.0
            matched_tokens: set[str] = set()
            for token in query_tokens:
                entry = self._index.get(token)
                if not entry:
                    continue
                tf = counts.get(token, 0)
                if not tf:
                    continue
                matched_tokens.add(token)
                denominator = tf + k1 * (1 - b + b * length / (self._avg_len or 1))
                score += entry["idf"] * (tf * (k1 + 1)) / denominator

            # Alias hits are strong signals: "ADIP", "UDID", "RPwD".
            lowered_query = query.lower()
            alias_hit = False
            for alias in scheme.get("aliases", []):
                if alias.lower() in lowered_query:
                    score += 4.0
                    alias_hit = True

            # One incidental shared word ("state", "document") is not evidence
            # that this is the scheme the user means. Require two distinct
            # content words, or an explicit alias match.
            if not alias_hit and len(matched_tokens) < 2:
                continue

            if score > 0:
                scored.append(ScoredScheme(scheme=scheme, score=round(score, 3)))

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def get(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        for scheme in self.schemes:
            if scheme["id"] == scheme_id:
                return scheme
        return None

    # ----------------------------------------------------------- eligibility
    def evaluate_eligibility(
        self, scheme: Dict[str, Any], profile: Optional[Profile]
    ) -> Dict[str, Any]:
        """Return ``eligible``, ``not_eligible`` or ``unknown`` plus reasons."""
        if profile is None:
            return {
                "status": "unknown",
                "reasons": ["No profile supplied, so eligibility cannot be checked."],
                "subsidy_percent": None,
            }

        rules = scheme.get("eligibility", {})
        reasons: List[str] = []
        failed = False
        unknown = False

        minimum = float(rules.get("disability_percent_min", 0) or 0)
        if minimum > 0:
            if profile.disability_percent is None:
                unknown = True
                reasons.append(f"Disability percentage is required (minimum {minimum:g}%).")
            elif profile.disability_percent < minimum:
                failed = True
                reasons.append(
                    f"Disability is {profile.disability_percent:g}%, below the {minimum:g}% minimum."
                )
            else:
                reasons.append(f"Disability is at or above the {minimum:g}% minimum.")

        if rules.get("requires_udid"):
            if profile.has_udid is None:
                unknown = True
                reasons.append("UDID card status is required.")
            elif not profile.has_udid:
                failed = True
                reasons.append("A UDID card or UDID enrolment number is required.")
            else:
                reasons.append("UDID requirement is met.")

        if rules.get("requires_aadhaar"):
            if profile.has_aadhaar is None:
                unknown = True
                reasons.append("Aadhaar status is required.")
            elif not profile.has_aadhaar:
                failed = True
                reasons.append("Aadhaar or an Aadhaar enrolment number is required.")
            else:
                reasons.append("Aadhaar requirement is met.")

        subsidy: Optional[float] = None
        slabs = rules.get("income_slabs") or []
        if slabs:
            if profile.monthly_income_inr is None:
                unknown = True
                reasons.append("Monthly family income is required to choose a subsidy slab.")
            else:
                for slab in slabs:
                    lower = slab.get("min_monthly_inr", 0)
                    upper = slab.get("max_monthly_inr")
                    if profile.monthly_income_inr >= lower and (
                        upper is None or profile.monthly_income_inr <= upper
                    ):
                        subsidy = float(slab["subsidy_percent"])
                        reasons.append(
                            f"Monthly income ₹{profile.monthly_income_inr:,.0f} falls in the "
                            f"{subsidy:g}% subsidy slab."
                        )
                        break
                if subsidy is None:
                    failed = True
                    reasons.append("Monthly income is above the highest subsidy slab.")

        if failed:
            status = "not_eligible"
        elif unknown:
            status = "unknown"
        else:
            status = "eligible"

        return {"status": status, "reasons": reasons, "subsidy_percent": subsidy}

    # ---------------------------------------------------------------- answers
    def answer(self, query: str, profile: Optional[Profile] = None) -> Dict[str, Any]:
        matches = self.search(query, top_k=3)
        if not matches or matches[0].score < MIN_SCORE:
            return {
                "found": False,
                "answer": (
                    "I could not find this in the verified scheme dataset. I will not "
                    "guess. Try the scheme name (ADIP, UDID, RPwD) or check "
                    "depwd.gov.in."
                ),
                "citations": [],
                "matches": [],
            }

        primary = matches[0].scheme
        eligibility = self.evaluate_eligibility(primary, profile)
        citations = [self._citation(item.scheme) for item in matches]

        lines: List[str] = [f"### {primary['name']}", "", primary["summary"], ""]

        if eligibility["status"] != "unknown":
            verdict = {
                "eligible": "Likely eligible",
                "not_eligible": "Not eligible on the facts supplied",
            }.get(eligibility["status"], "Needs more information")
            lines.append(f"**Eligibility check:** {verdict}.")
            for reason in eligibility["reasons"]:
                lines.append(f"- {reason}")
            if eligibility["subsidy_percent"] is not None:
                lines.append(f"- Subsidy: **{eligibility['subsidy_percent']:g}%**")
            lines.append("")
        elif profile is None:
            lines.append("**Eligibility check:** not run. Add your details to check.")
            lines.append("")

        lines.append("**What you get**")
        for benefit in primary.get("benefits", []):
            lines.append(f"- {benefit}")
        lines.append("")

        documents = primary.get("documents_required", [])
        if documents:
            lines.append("**Documents to carry**")
            for document in documents:
                lines.append(f"- {document}")
            lines.append("")

        lines.append("**How to apply**")
        for step in primary.get("how_to_apply", []):
            lines.append(f"- {step}")
        lines.append("")

        stale = self._is_stale(primary)
        lines.append("---")
        lines.append(
            f"Source: {primary['source_url']}  \n"
            f"Last verified: {primary['last_verified']}  \n"
            f"Review due: {primary['review_due']}  \n"
            f"Status: {primary['verification_status']}"
        )
        if stale:
            lines.append(
                "\n> **This record is past its review date.** Confirm the current "
                "income limits and benefit caps on the official portal before applying."
            )
        if primary.get("helpline"):
            lines.append(f"\nHelpline: {primary['helpline']}")
        lines.append(
            "\n_This is an information aid, not a legal or financial decision. "
            "The official portal is the final authority._"
        )

        return {
            "found": True,
            "answer": "\n".join(lines),
            "citations": citations,
            "matches": [
                {"id": item.scheme["id"], "name": item.scheme["name"], "score": item.score}
                for item in matches
            ],
            "eligibility": eligibility,
        }

    @staticmethod
    def _citation(scheme: Dict[str, Any]) -> Dict[str, str]:
        return {
            "id": scheme["id"],
            "name": scheme["name"],
            "source_url": scheme["source_url"],
            "last_verified": scheme["last_verified"],
            "review_due": scheme["review_due"],
        }

    @staticmethod
    def _is_stale(scheme: Dict[str, Any]) -> bool:
        try:
            due = datetime.strptime(scheme["review_due"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            return True
        return due < date.today()

    def validation_errors(self) -> List[str]:
        """Cheap structural checks used by tests and CI."""
        errors: List[str] = []
        required = {
            "id", "name", "aliases", "category", "jurisdiction", "summary",
            "eligibility", "benefits", "documents_required", "how_to_apply",
            "portal_url", "source_url", "last_verified", "review_due",
            "verification_status", "notes",
        }
        seen: set[str] = set()
        for scheme in self.schemes:
            missing = required - set(scheme)
            if missing:
                errors.append(f"{scheme.get('id', '?')}: missing {sorted(missing)}")
            scheme_id = scheme.get("id", "")
            if scheme_id in seen:
                errors.append(f"duplicate id: {scheme_id}")
            seen.add(scheme_id)
            if not str(scheme.get("source_url", "")).startswith("http"):
                errors.append(f"{scheme_id}: source_url must be an http(s) URL")
            try:
                datetime.strptime(scheme.get("last_verified", ""), "%Y-%m-%d")
                datetime.strptime(scheme.get("review_due", ""), "%Y-%m-%d")
            except ValueError:
                errors.append(f"{scheme_id}: dates must be YYYY-MM-DD")
        return errors
