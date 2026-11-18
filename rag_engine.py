"""
Sahaaya AI - retrieval engine for the Streamlit prototype.

This module is part of the **legacy prototype** kept for reference. The
production client is the Android app in ``android/`` and the citation-backed
retrieval code lives in ``ml/rag/``.

What changed in the refactor (see docs/CLAIMS_MATRIX.md):
  * the tokenizer no longer drops short numeric tokens such as ``10``/``20``/``50``
  * speech is no longer truncated at 400 characters
  * the retired ``gemini-1.5-flash`` model and the deprecated
    ``google-generativeai`` package are gone; the model is configurable
  * answers carry structured citations and an explicit "not found" path
  * the prompt no longer asks the model to claim counterfeit detection
"""

from __future__ import annotations

import json
import math
import os
import re
from io import BytesIO
from typing import Any, Dict, List, Optional

try:  # optional dependency
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised only when gTTS is absent
    GTTS_AVAILABLE = False

try:  # new, supported Google Gen AI SDK
    from google import genai

    GEMINI_AVAILABLE = True
except ImportError:  # pragma: no cover
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:  # pragma: no cover
    OPENAI_AVAILABLE = False


#: Languages the prototype can actually synthesise speech for.
TTS_LANGUAGES = {
    "Hindi": "hi",
    "English": "en",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Bengali": "bn",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Gujarati": "gu",
}

#: Model is configurable. Do not hard-code a retired model name again.
DEFAULT_LLM_MODEL = os.getenv("SAHAAYA_LLM_MODEL", "gemini-2.0-flash")

#: Below this cosine score the engine refuses to answer from the knowledge base.
MIN_RETRIEVAL_SCORE = 0.08

#: Function words that carry no evidence. A query made only of these must not
#: retrieve a scheme, and a single incidental shared word is not proof that the
#: question is about that document. Mirrors ``scheme_engine.STOPWORDS``.
STOPWORDS = {
    "a", "about", "also", "an", "and", "any", "are", "as", "at", "be", "by", "can", "do",
    "does", "exactly", "for", "from", "get", "give", "how", "i", "if", "in", "into", "is",
    "it", "its", "me", "much", "my", "no", "not", "of", "on", "or", "per", "please", "some",
    "that", "the", "there", "these", "this", "those", "to", "under", "what", "when", "where",
    "which", "who", "will", "with", "you",
}

#: Conservative cap so a long document cannot exhaust memory in a demo.
MAX_TTS_CHARS = 6000
TTS_CHUNK_CHARS = 180


class SahaayaRAGEngine:
    """TF-IDF retrieval over the prototype knowledge base.

    This is lexical retrieval, not a neural retriever. It is labelled as such
    everywhere it is shown to a user.
    """

    def __init__(self, kb_dir: str = "knowledge_base"):
        self.kb_dir = kb_dir
        self.chunks: List[Dict[str, Any]] = []
        self.idf: Dict[str, float] = {}
        self.chunk_vectors: List[Dict[str, float]] = []
        self.load_knowledge_base()
        self.build_index()

    # ------------------------------------------------------------------ text
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenise while preserving denominations.

        ``₹10``, ``Rs 10``, ``10``, ``10/-`` and ``ten`` must all keep a
        signal. The previous implementation dropped every token with two or
        fewer characters, which silently removed 10, 20 and 50 from currency
        questions.
        """
        lowered = text.lower()
        lowered = lowered.replace("₹", " ").replace("rs.", " ").replace("rs", " ")
        lowered = re.sub(r"[^\w\s/]", " ", lowered)
        tokens: List[str] = []
        for raw in lowered.split():
            token = raw.strip("/")
            if not token:
                continue
            # keep alphanumerics and any token that contains a digit
            if len(token) == 1 and not token.isdigit():
                continue
            tokens.append(token)
        return tokens

    # ------------------------------------------------------------------- data
    def load_knowledge_base(self) -> None:
        self.chunks = []
        if not os.path.isdir(self.kb_dir):
            return

        for fname in sorted(os.listdir(self.kb_dir)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self.kb_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as handle:
                    self._parse_json_to_chunks(fname, json.load(handle))
            except (OSError, json.JSONDecodeError) as exc:
                print(f"Could not load {fname}: {exc}")

    def _parse_json_to_chunks(self, source_file: str, data: Any) -> None:
        if not isinstance(data, dict):
            return

        if "demographics" in data:
            demo = data["demographics"]
            self.chunks.append(
                {
                    "source": "Census 2011 / NSS / LASI (see data file for notes)",
                    "title": "National disability rates in India",
                    "content": (
                        f"India population estimate: {demo.get('total_population_estimate_2026')}. "
                        f"Disability rate: {demo.get('overall_disability_percentage')}. "
                        f"Visual impairment: {demo.get('visual_impairment_seeing')}. "
                        f"Hearing impairment: {demo.get('hearing_impairment')}. "
                        f"Speech impairment: {demo.get('speech_impairment_mute')}."
                    ),
                }
            )
            self.chunks.append(
                {
                    "source": "WHO-UNICEF GReAT report",
                    "title": "Assistive technology gap and out-of-pocket burden",
                    "content": (
                        f"Unmet assistive technology need: {demo.get('unmet_technology_need')}. "
                        f"Out-of-pocket spending: {demo.get('out_of_pocket_crisis')}. "
                        f"Rural divide: {demo.get('rural_divide')}."
                    ),
                }
            )
            for state in demo.get("top_states_by_disability_burden", []):
                self.chunks.append(
                    {
                        "source": f"State profile: {state.get('state', 'unknown')}",
                        "title": f"Disability burden in {state.get('state', 'unknown')}",
                        "content": (
                            f"State: {state.get('state')} (rank {state.get('rank')}). "
                            f"Share: {state.get('national_share')}. "
                            f"Key challenges: {state.get('key_challenges')}"
                        ),
                    }
                )

        if "schemes_and_rights" in data:
            for scheme in data["schemes_and_rights"]:
                provisions = " ".join(scheme.get("key_provisions", [])) or " ".join(
                    scheme.get("benefits", [])
                )
                devices = " ".join(scheme.get("covered_devices", []))
                self.chunks.append(
                    {
                        "source": f"Scheme: {scheme.get('name', 'unknown')}",
                        "title": scheme.get("name", "Untitled scheme"),
                        "url": scheme.get("source_url") or scheme.get("portal_url", ""),
                        "verified": scheme.get("last_verified", ""),
                        "content": (
                            f"{scheme.get('name')}: {scheme.get('overview', '')} "
                            f"{provisions} {devices} "
                            f"Eligibility: {scheme.get('eligibility', 'Not stated')}. "
                            f"Portal: {scheme.get('portal_url', '')} "
                            f"Helpline: {scheme.get('national_helpline', '')} "
                            f"Last verified: {scheme.get('last_verified', 'unknown')}"
                        ),
                    }
                )

        if "existing_technologies_and_gaps" in data:
            for item in data["existing_technologies_and_gaps"]:
                drawbacks = " ".join(item.get("critical_drawbacks", [])) or item.get(
                    "gaps_in_practice", ""
                )
                self.chunks.append(
                    {
                        "source": f"Technology note: {item.get('technology', 'unknown')}",
                        "title": f"Gaps in {item.get('technology', 'unknown')}",
                        "content": (
                            f"Technology: {item.get('technology')} by {item.get('developer', '')}. "
                            f"Purpose: {item.get('intended_purpose', '')}. "
                            f"Documented gaps: {drawbacks}"
                        ),
                    }
                )

    # ------------------------------------------------------------------ index
    def build_index(self) -> None:
        # Acronyms in a chunk title (ADIP, UDID, RPwD) are explicit references to
        # that document. A query that names one is evidence enough on its own.
        self.aliases: set[str] = set()
        for chunk in self.chunks:
            for word in re.findall(r"[A-Za-z]*[A-Z][A-Za-z]*[A-Z][A-Za-z]*", chunk.get("title", "")):
                if len(word) >= 3:
                    self.aliases.add(word.lower())
        if not self.chunks:
            self.idf = {}
            self.chunk_vectors = []
            return

        doc_count = len(self.chunks)
        doc_frequencies: Dict[str, int] = {}
        tokenised: List[List[str]] = []

        for chunk in self.chunks:
            tokens = self.tokenize(f"{chunk['title']} {chunk['content']}")
            tokenised.append(tokens)
            for token in set(tokens):
                doc_frequencies[token] = doc_frequencies.get(token, 0) + 1

        self.idf = {
            token: math.log((doc_count + 1) / (frequency + 1)) + 1.0
            for token, frequency in doc_frequencies.items()
        }

        self.chunk_vectors = [self._vectorise(tokens) for tokens in tokenised]

    def _vectorise(self, tokens: List[str]) -> Dict[str, float]:
        vector: Dict[str, float] = {}
        for token in tokens:
            vector[token] = vector.get(token, 0.0) + 1.0
        norm = 0.0
        for token, count in vector.items():
            weight = count * self.idf.get(token, 1.0)
            vector[token] = weight
            norm += weight * weight
        norm = math.sqrt(norm) or 1.0
        return {token: weight / norm for token, weight in vector.items()}

    # --------------------------------------------------------------- retrieval
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        tokens = self.tokenize(query)
        if not tokens or not self.chunk_vectors:
            return []

        query_vector = self._vectorise(tokens)
        scored = []
        for index, chunk_vector in enumerate(self.chunk_vectors):
            score = sum(
                chunk_vector.get(token, 0.0) * weight
                for token, weight in query_vector.items()
            )
            scored.append((score, index))

        scored.sort(key=lambda item: item[0], reverse=True)
        results: List[Dict[str, Any]] = []
        for score, index in scored[:top_k]:
            chunk = dict(self.chunks[index])
            chunk["score"] = round(score, 4)
            results.append(chunk)
        return results

    # ---------------------------------------------------------------- answers
    def _has_enough_evidence(self, query: str, chunk: Dict[str, Any]) -> bool:
        """Does the query share real content with this chunk?

        A single incidental shared word ("capital" in "capital subsidy") is not
        evidence that an unrelated question is covered by this document. Require
        two distinct content words, or one content word when the query itself
        is a single term such as "UDID".
        """
        query_tokens = {token for token in self.tokenize(query) if token not in STOPWORDS}
        if not query_tokens:
            return False
        if query_tokens & self.aliases:
            return True
        chunk_text = f"{chunk.get('title', '')} {chunk.get('content', '')}"
        overlap = query_tokens & set(self.tokenize(chunk_text))
        if len(query_tokens) == 1:
            return bool(overlap)
        return len(overlap) >= 2

    def generate_answer(
        self,
        query: str,
        lang: str = "English",
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        retrieved = self.retrieve(query, top_k=3)
        best_score = retrieved[0]["score"] if retrieved else 0.0

        if (
            not retrieved
            or best_score < MIN_RETRIEVAL_SCORE
            or not self._has_enough_evidence(query, retrieved[0])
        ):
            return {
                "answer": (
                    "I could not find this in the verified knowledge base, so I will not "
                    "guess. Please check the official portal, or rephrase the question "
                    "using a scheme name such as ADIP, UDID or RPwD."
                ),
                "sources": [],
                "citations": [],
                "engine": "Retrieval only (no answer found)",
                "found": False,
            }

        citations = [
            {
                "title": item["title"],
                "source": item["source"],
                "url": item.get("url", ""),
                "verified": item.get("verified", ""),
                "score": item["score"],
            }
            for item in retrieved
        ]
        context = "\n\n".join(
            f"[{item['source']} - {item['title']}]\n{item['content']}" for item in retrieved
        )

        system_prompt = f"""
You are Sahaaya AI, an accessibility information assistant for India.
Answer in {lang}. Use only the grounding context below.
Rules:
- If the context does not contain the answer, say so. Do not invent eligibility rules.
- Never claim that the app detects counterfeit notes or guarantees a safe walking path.
- Never state a benefit amount without the last-verified date.
- End with the source names you used.
- Keep sentences short; the answer may be read aloud by a screen reader.

Grounding context:
{context}
"""

        if gemini_api_key and GEMINI_AVAILABLE:
            try:
                client = genai.Client(api_key=gemini_api_key)
                response = client.models.generate_content(
                    model=DEFAULT_LLM_MODEL,
                    contents=f"{system_prompt}\n\nQuestion: {query}\n\nAnswer in {lang}:",
                )
                if response.text:
                    return {
                        "answer": response.text,
                        "sources": [item["source"] for item in retrieved],
                        "citations": citations,
                        "engine": f"Google Gen AI ({DEFAULT_LLM_MODEL}), retrieval-grounded",
                        "found": True,
                    }
            except Exception as exc:  # noqa: BLE001 - surface, then fall back
                print(f"Gemini generation error: {exc}")

        if openai_api_key and OPENAI_AVAILABLE:
            try:
                client = OpenAI(api_key=openai_api_key)
                response = client.chat.completions.create(
                    model=os.getenv("SAHAAYA_OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query},
                    ],
                    temperature=0.2,
                )
                text = response.choices[0].message.content
                if text:
                    return {
                        "answer": text,
                        "sources": [item["source"] for item in retrieved],
                        "citations": citations,
                        "engine": "OpenAI (retrieval-grounded)",
                        "found": True,
                    }
            except Exception as exc:  # noqa: BLE001
                print(f"OpenAI generation error: {exc}")

        # Extractive fallback: show the retrieved text, not a fabricated summary.
        lines = [f"### Retrieved from the knowledge base for: *\"{query}\"*\n"]
        for item in retrieved:
            verified = f" (last verified: {item['verified']})" if item.get("verified") else ""
            lines.append(f"**{item['title']}** - {item['source']}{verified}\n\n{item['content']}\n")
        lines.append(
            "\nThis is an extract, not a generated answer. Confirm eligibility on the "
            "official portal before applying."
        )

        return {
            "answer": "\n".join(lines),
            "sources": [item["source"] for item in retrieved],
            "citations": citations,
            "engine": "Extractive retrieval (no LLM configured)",
            "found": True,
        }

    # -------------------------------------------------------------------- TTS
    @staticmethod
    def _speech_chunks(text: str) -> List[str]:
        clean = re.sub(r"https?://\S+", " ", text)
        clean = re.sub(r"[*#_`>|]", " ", clean)
        clean = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", clean)
        clean = re.sub(r"\s+", " ", clean).strip()[:MAX_TTS_CHARS]
        if not clean:
            return []

        sentences = re.split(r"(?<=[.!?।])\s+", clean)
        chunks: List[str] = []
        current = ""
        for sentence in sentences:
            if not sentence:
                continue
            if len(current) + len(sentence) + 1 <= TTS_CHUNK_CHARS:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    chunks.append(current)
                while len(sentence) > TTS_CHUNK_CHARS:
                    chunks.append(sentence[:TTS_CHUNK_CHARS])
                    sentence = sentence[TTS_CHUNK_CHARS:]
                current = sentence
        if current:
            chunks.append(current)
        return chunks

    def text_to_speech_audio(
        self, text: str, lang_code: str = "hi", speed: float = 1.0
    ) -> Optional[BytesIO]:
        """Return a spoken version of ``text``.

        Long answers are split into sentence-sized chunks and concatenated
        instead of being cut at 400 characters.
        """
        if not GTTS_AVAILABLE:
            return None

        code = TTS_LANGUAGES.get(lang_code, lang_code)
        chunks = self._speech_chunks(text)
        if not chunks:
            return None

        try:
            audio = BytesIO()
            for chunk in chunks:
                tts = gTTS(text=chunk, lang=code, slow=speed < 0.85, tld="co.in")
                tts.write_to_fp(audio)
            audio.seek(0)
            return audio
        except Exception as exc:  # noqa: BLE001 - network/voice failures are expected
            print(f"gTTS error: {exc}")
            return None
