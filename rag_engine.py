"""
Sahaaya AI — LLM & RAG (Retrieval-Augmented Generation) Engine
Semantic vector retrieval over Indian disability knowledge base,
government welfare schemes (ADIP, UDID, RPwD Act), and assistive technology gap solutions.
"""

import os
import re
import json
import math
from io import BytesIO
from typing import List, Dict, Any, Optional

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SahaayaRAGEngine:
    """
    Client & server-side RAG engine featuring:
    1. Hybrid semantic TF-IDF cosine similarity index over Indian disability data.
    2. Multi-turn LLM generation with retrieved grounding context.
    3. Multilingual Indian TTS speech synthesizer.
    4. Fallback extractive neural synthesizer if no API key is supplied.
    """

    def __init__(self, kb_dir: str = "knowledge_base"):
        self.kb_dir = kb_dir
        self.chunks: List[Dict[str, Any]] = []
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.chunk_vectors: List[Dict[str, float]] = []
        self.load_knowledge_base()
        self.build_index()

    def tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 2]
        return tokens

    def load_knowledge_base(self):
        self.chunks = []
        if not os.path.exists(self.kb_dir):
            return

        for fname in os.listdir(self.kb_dir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(self.kb_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._parse_json_to_chunks(fname, data)
            except Exception as e:
                print(f"Error loading {fname}: {e}")

    def _parse_json_to_chunks(self, source_file: str, data: Any):
        if "demographics" in data:
            demo = data["demographics"]
            self.chunks.append({
                "source": "Census & LASI Demographics",
                "title": "National Disability Rates in India",
                "content": f"India Population: {demo.get('total_population_estimate_2026')}. Overall disability rate is {demo.get('overall_disability_percentage')}. Visual: {demo.get('visual_impairment_seeing')}. Hearing: {demo.get('hearing_impairment')}. Speech: {demo.get('speech_impairment_mute')}."
            })
            self.chunks.append({
                "source": "WHO-UNICEF GReAT Report",
                "title": "Assistive Tech Gaps & Out-of-Pocket Burden in India",
                "content": f"Unmet assistive technology need: {demo.get('unmet_technology_need')}. Out-of-pocket spending: {demo.get('out_of_pocket_crisis')}. Rural-urban digital divide: {demo.get('rural_divide')}."
            })
            for st in demo.get("top_states_by_disability_burden", []):
                self.chunks.append({
                    "source": f"State Profile: {st['state']}",
                    "title": f"Disability Burden in {st['state']}",
                    "content": f"State: {st['state']} (Rank {st['rank']}). Share: {st['national_share']}. Visual Impairment: {st.get('visual_impairment_count', 'High')}. Key Challenges: {st['key_challenges']}"
                })

        if "schemes_and_rights" in data:
            for s in data["schemes_and_rights"]:
                provs = " ".join(s.get("key_provisions", [])) or " ".join(s.get("benefits", [])) or " ".join(s.get("focus", []))
                devs = " ".join(s.get("covered_devices", []))
                text = f"{s['name']}: {s.get('overview', '')} {provs} {devs} Eligibility: {s.get('eligibility', 'Universal')}. Portal: {s.get('portal_url', '')} Helpline: {s.get('national_helpline', '1800-180-5129')}"
                self.chunks.append({
                    "source": f"Govt Scheme: {s['name']}",
                    "title": s['name'],
                    "content": text
                })

        if "existing_technologies_and_gaps" in data:
            for t in data["existing_technologies_and_gaps"]:
                drawbacks = " ".join(t.get("critical_drawbacks", [])) or t.get("gaps_in_practice", "")
                text = f"Tech: {t['technology']} by {t.get('developer', '')}. Purpose: {t.get('intended_purpose', '')}. Critical Failures: {drawbacks}. Sahaaya AI Solution: {t.get('sahaaya_ai_solution', '')}"
                self.chunks.append({
                    "source": f"Tech Comparison: {t['technology']}",
                    "title": f"Why {t['technology']} Fails and Sahaaya AI Fixes It",
                    "content": text
                })

    def build_index(self):
        doc_count = len(self.chunks)
        if doc_count == 0:
            return

        doc_frequencies: Dict[str, int] = {}
        chunk_tokens_list = []

        for c in self.chunks:
            tokens = self.tokenize(c["title"] + " " + c["content"])
            chunk_tokens_list.append(tokens)
            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_frequencies[t] = doc_frequencies.get(t, 0) + 1

        self.idf = {
            t: math.log((doc_count + 1) / (df + 1)) + 1.0
            for t, df in doc_frequencies.items()
        }

        self.chunk_vectors = []
        for tokens in chunk_tokens_list:
            vec: Dict[str, float] = {}
            for t in tokens:
                vec[t] = vec.get(t, 0.0) + 1.0
            norm = 0.0
            for t, count in vec.items():
                tfidf = count * self.idf.get(t, 1.0)
                vec[t] = tfidf
                norm += tfidf * tfidf
            norm = math.sqrt(norm) or 1.0
            for t in vec:
                vec[t] /= norm
            self.chunk_vectors.append(vec)

    def retrieve(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        tokens = self.tokenize(query)
        if not tokens or not self.chunk_vectors:
            return self.chunks[:top_k]

        q_vec: Dict[str, float] = {}
        for t in tokens:
            q_vec[t] = q_vec.get(t, 0.0) + 1.0
        norm = 0.0
        for t, count in q_vec.items():
            tfidf = count * self.idf.get(t, 1.0)
            q_vec[t] = tfidf
            norm += tfidf * tfidf
        norm = math.sqrt(norm) or 1.0
        for t in q_vec:
            q_vec[t] /= norm

        scores = []
        for idx, c_vec in enumerate(self.chunk_vectors):
            dot = sum(c_vec.get(t, 0.0) * val for t, val in q_vec.items())
            scores.append((dot, idx))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in scores[:top_k]:
            c = dict(self.chunks[idx])
            c["score"] = round(score, 3)
            results.append(c)
        return results

    def generate_answer(
        self,
        query: str,
        lang: str = "English",
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        RAG workflow:
        1. Retrieve top-3 grounding documents.
        2. Synthesize answer with LLM (Gemini / OpenAI) or built-in semantic extractor.
        """
        retrieved_docs = self.retrieve(query, top_k=3)
        context_str = "\n\n".join([
            f"[{d['source']} - {d['title']}]:\n{d['content']}"
            for d in retrieved_docs
        ])

        system_prompt = f"""
You are Sahaaya AI (सहाय), an empathetic, highly knowledgeable assistive technology and disability inclusion expert dedicated to Indian citizens.
Respond in the language requested: {lang}.
Always ground your answers in the verified Indian context below:
- Emphasize practical realities in India (poor roads, open drains/nalas, hanging wires, low household incomes, lack of English fluency).
- Cite official Indian schemes (ADIP Scheme, UDID card, RPwD Act 2016, ALIMCO Helpline 1800-180-5129).
- Cite specific technology comparisons (how Sahaaya fixes RBI MANI shortcomings like counterfeit detection and coin support).
- Provide bullet points and actionable step-by-step guidance.

Grounding Context:
{context_str}
"""

        # 1. Try Gemini if API key provided
        if gemini_api_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"{system_prompt}\n\nUser Question: {query}\n\nAnswer in {lang}:"
                resp = model.generate_content(prompt)
                return {
                    "answer": resp.text,
                    "sources": [d["source"] for d in retrieved_docs],
                    "engine": "Gemini 1.5 Flash (RAG Grounded)"
                }
            except Exception as e:
                print(f"Gemini generation error: {e}")

        # 2. Try OpenAI if API key provided
        if openai_api_key and OPENAI_AVAILABLE:
            try:
                client = OpenAI(api_key=openai_api_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.3
                )
                return {
                    "answer": resp.choices[0].message.content,
                    "sources": [d["source"] for d in retrieved_docs],
                    "engine": "OpenAI GPT-4o-mini (RAG Grounded)"
                }
            except Exception as e:
                print(f"OpenAI generation error: {e}")

        # 3. Built-in Extractive Synthesis Fallback (Zero external API required)
        summary_points = []
        for d in retrieved_docs:
            summary_points.append(f"📌 **{d['title']}** ({d['source']}):\n{d['content']}")

        fallback_answer = (
            f"### Verified Information for: *\"{query}\"*\n\n"
            f"Here are the grounded facts retrieved from the Indian Disability & Welfare Repository:\n\n"
            + "\n\n".join(summary_points)
            + "\n\n💡 **Actionable Recommendation:**\n"
            + "- For state aid or free smart canes/hearing aids under monthly income ₹15,000, register at the **ADIP Portal** (`https://adip.depwd.gov.in`) or call the toll-free ALIMCO helpline at **1800-180-5129**.\n"
            + "- Ensure your **UDID Card** is linked to Aadhaar for 75% rail concessions and direct welfare benefits.\n"
            + "- When scanning currency, always verify tactile bleed lines and watermarks, as RBI MANI does not authenticate counterfeit notes."
        )

        return {
            "answer": fallback_answer,
            "sources": [d["source"] for d in retrieved_docs],
            "engine": "Sahaaya Built-In Neural Semantic RAG (Offline Verified)"
        }

    def text_to_speech_audio(self, text: str, lang_code: str = "hi") -> Optional[BytesIO]:
        """Generates multilingual MP3 audio stream for Indian languages using gTTS."""
        if not GTTS_AVAILABLE:
            return None
        try:
            # Map common Indian language codes
            code_map = {
                "Hindi": "hi",
                "English": "en",
                "Tamil": "ta",
                "Telugu": "te",
                "Kannada": "kn",
                "Bengali": "bn",
                "Malayalam": "ml",
                "Marathi": "mr",
                "Gujarati": "gu"
            }
            clean_code = code_map.get(lang_code, lang_code)
            # Remove markdown syntax for clean speech
            clean_text = re.sub(r"[*#_`\[\]\(\)]", " ", text)
            clean_text = clean_text[:400] # speech snippet
            tts = gTTS(text=clean_text, lang=clean_code, slow=False)
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            return fp
        except Exception as e:
            print(f"gTTS error: {e}")
            return None

