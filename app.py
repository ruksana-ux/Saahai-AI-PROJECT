"""
Sahaaya AI - legacy Streamlit prototype.

STATUS: prototype / archive. This is **not** the production client.

The production product is the Android app in ``android/``. Streamlit reruns the
whole script on every interaction, captures still frames, and cannot deliver a
sub-200 ms camera-to-haptic loop, so it is kept only as a browser demo of the
models and the scheme dataset.

Every screen below is written to avoid the overclaims in the previous version.
See docs/CLAIMS_MATRIX.md for the claim-by-claim status.
"""

from __future__ import annotations

import os

import streamlit as st
from PIL import Image

from aac_engine import SahaayaAACEngine
from classroom_engine import SahaayaClassroomEngine
from currency_engine import SahaayaCurrencyEngine
from document_engine import read_document
from isl_engine import SahaayaISLEngine
from rag_engine import TTS_LANGUAGES, SahaayaRAGEngine
from scheme_engine import Profile, SchemeEngine

st.set_page_config(
    page_title="Sahaaya Drishti - prototype",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)


def secret(name: str) -> str:
    """Read a secret without crashing when secrets.toml is absent.

    ``st.secrets.get`` raises ``StreamlitSecretNotFoundError`` (a
    ``FileNotFoundError``) when no secrets file exists, so ``hasattr`` and
    ``.get`` are both insufficient. Environment variables are the fallback.
    """
    try:
        value = st.secrets.get(name, "")
    except Exception:  # noqa: BLE001 - missing/invalid secrets file
        value = ""
    return str(value or os.getenv(name, ""))


@st.cache_resource
def load_engines():
    return {
        "rag": SahaayaRAGEngine(kb_dir="knowledge_base"),
        "schemes": SchemeEngine(),
        "currency": SahaayaCurrencyEngine(),
        "classroom": SahaayaClassroomEngine(),
        "isl": SahaayaISLEngine(),
        "aac": SahaayaAACEngine(),
    }


engines = load_engines()
rag = engines["rag"]
schemes = engines["schemes"]
currency = engines["currency"]
classroom = engines["classroom"]
isl = engines["isl"]
aac = engines["aac"]

st.markdown(
    """
    <style>
      .sd-banner { background:#0b3d3a; color:#fff; padding:18px 22px; border-radius:12px; }
      .sd-banner h1 { margin:0; font-size:1.7rem; }
      .sd-banner p { margin:6px 0 0; opacity:.9; }
      .sd-note { background:#fff8e1; border-left:5px solid #b26a00; padding:10px 14px; border-radius:6px; }
      .sd-cite { background:#eef4f3; border-left:5px solid #00796b; padding:10px 14px; border-radius:6px; font-size:.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sd-banner">
      <h1>Sahaaya Drishti <span aria-hidden="true">·</span> सहाय दृष्टि</h1>
      <p>Browser prototype for Indian currency, documents and disability schemes.
      The production app is the offline-first Android client in <code>android/</code>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sd-note"><b>Prototype notice.</b> This page is a demo, not a '
    "mobility aid, not a counterfeit detector, and not a substitute for the "
    "official scheme portal. Do not rely on it for safety decisions.</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Controls")
    language = st.selectbox(
        "Voice language",
        list(TTS_LANGUAGES.keys()),
        index=0,
        help="Speech output only. The AAC board supports English, Hindi, Tamil, Telugu and Kannada.",
    )

    st.markdown("---")
    st.subheader("Optional language model")
    gemini_key = secret("GEMINI_API_KEY")
    openai_key = secret("OPENAI_API_KEY")
    gemini_input = st.text_input(
        "Google Gen AI API key (optional)", value=gemini_key, type="password"
    )
    openai_input = st.text_input(
        "OpenAI API key (optional)", value=openai_key, type="password"
    )
    if gemini_input or openai_input:
        st.success("A language model is configured. Scheme eligibility is still rule-based.")
    else:
        st.info("No LLM configured. Answers are extracts from the verified dataset.")

    st.markdown("---")
    st.subheader("What this build can do")
    st.markdown(
        "- Currency: real TFLite model if one is installed, otherwise it says so.\n"
        "- Documents: offline OCR if RapidOCR or Tesseract is installed.\n"
        "- Schemes: BM25 retrieval plus a rules engine, with citations.\n"
        "- Emergency: dials 112. No automatic location is sent."
    )

    st.markdown("---")
    st.caption(
        "Legacy demo kept for reference. Production target: Android 8+, 2 GB RAM, "
        "airplane mode."
    )

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
currency_tab, document_tab, scheme_tab, archive_tab, safety_tab = st.tabs(
    [
        "💵 Currency",
        "📄 Documents",
        "🏛️ Schemes",
        "🗂️ Out-of-scope archive",
        "🛡️ Safety & status",
    ]
)

# ===========================================================================
# Currency
# ===========================================================================
with currency_tab:
    st.subheader("Indian banknotes and coins")
    st.write(
        "Identify a denomination. This is an **identification aid**, not an "
        "authentication device: it cannot tell you whether a note is genuine."
    )

    if currency.model_available:
        st.success(f"Currency model loaded: `{currency.model_path}`")
    else:
        st.warning(
            "**No trained currency model is installed in this build.** "
            "The app will not guess a denomination. Run `ml/currency/train.py` "
            "and copy the exported model to `models/currency/`."
        )

    left, right = st.columns([1, 1])
    with left:
        camera_image = st.camera_input("Photograph a note or coin")
        uploaded = st.file_uploader(
            "Or upload a photo", type=["jpg", "jpeg", "png"], key="currency_upload"
        )
        source = camera_image or uploaded

    with right:
        if source:
            image = Image.open(source)
            st.image(image, caption="Input frame", use_container_width=True)
            result = currency.classify_image(image)

            status = result["status"]
            if status == "model_unavailable":
                st.error(result["message"])
            elif status == "model_error":
                # No confidence exists for this frame, so it must not fall
                # through to the success branch below.
                st.error(result["message"])
            elif status == "unknown":
                st.warning(
                    "This does not look like a supported Indian note or coin. "
                    "Reframe and try again."
                )
            elif status == "uncertain":
                top2 = ", ".join(
                    f"{item['label']} ({item['probability'] * 100:.0f}%)"
                    for item in result["top2"]
                )
                st.warning(
                    "**Not confident enough to state a denomination.** "
                    f"Best guesses: {top2}. Please rescan in better light, or use "
                    "the tactile check below."
                )
            else:
                st.success(f"**{result['denomination']}**")
                st.caption(
                    f"Model confidence: {result['confidence'] * 100:.1f}% "
                    f"(top-2 margin {result['margin'] * 100:.1f}%)"
                )

            spec = result.get("spec")
            if spec:
                st.markdown(f"**Tactile check:** {spec['tactile_mark']}")
                if spec["kind"] == "note":
                    st.caption(
                        f"RBI series: {spec['series']} · colour: {spec['colour']} · "
                        f"motif: {spec['motif']}"
                    )
            st.info(result["disclaimer"])

            if st.button("🔊 Speak result", key="speak_currency"):
                spoken = result["denomination"] or result["message"]
                audio = rag.text_to_speech_audio(spoken, language)
                if audio:
                    st.audio(audio, format="audio/mp3")
                else:
                    st.warning("Speech is unavailable (gTTS is not installed).")
        else:
            st.info("Add a photo, or open the manual tactile guide below.")

    with st.expander("Manual tactile guide (works without a model)"):
        key = st.selectbox(
            "Denomination",
            list(currency.CURRENCY_SPECS.keys()),
            format_func=lambda item: currency.CURRENCY_SPECS[item]["name"],
        )
        spec = currency.CURRENCY_SPECS[key]
        st.write(f"**{spec['name']}** — {spec['series']}")
        st.write(spec["tactile_mark"])
        if spec["kind"] == "note" and spec["bleed_lines"]:
            st.write(f"Bleed lines: **{spec['bleed_lines']}**")
        st.caption(
            "Tactile marks checked against RBI's 'For Visually Impaired' page on "
            "2026-11-18. Coins are described by shape and relative size only."
        )

# ===========================================================================
# Documents
# ===========================================================================
with document_tab:
    st.subheader("Read a printed document aloud")
    st.write(
        "Offline OCR with layout-aware reading order. For Hindi, Tamil, Telugu, "
        "Kannada, Malayalam, Bengali, Marathi and Gujarati, install the matching "
        "Tesseract language pack; RapidOCR's bundled model is Latin-script first."
    )

    doc_left, doc_right = st.columns([1, 1])
    with doc_left:
        doc_camera = st.camera_input("Photograph a page", key="doc_camera")
        doc_upload = st.file_uploader(
            "Or upload a page", type=["jpg", "jpeg", "png"], key="doc_upload"
        )
        doc_source = doc_camera or doc_upload
        tesseract_lang = st.selectbox(
            "OCR language",
            ["eng", "hin", "tam", "tel", "kan", "mal", "ben", "mar", "guj"],
            index=0,
            help="Used when Tesseract is the active engine.",
        )

    with doc_right:
        if doc_source:
            page = Image.open(doc_source)
            st.image(page, caption="Page", use_container_width=True)
            result = read_document(page, lang=tesseract_lang)

            if result["status"] == "engine_unavailable":
                st.error(result["warning"])
            else:
                quality = result["quality"]
                st.caption(
                    f"Engine: {result['engine']} · blur score {quality['blur_score']} · "
                    f"glare {quality['glare_ratio'] * 100:.1f}%"
                )
                if result["warning"]:
                    st.warning(result["warning"])

                text = st.text_area(
                    "Recognised text (editable)", value=result["text"], height=260
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🔊 Read aloud", key="speak_document"):
                        audio = rag.text_to_speech_audio(text, language)
                        if audio:
                            st.audio(audio, format="audio/mp3")
                        else:
                            st.warning("Speech is unavailable (gTTS is not installed).")
                with col_b:
                    st.download_button(
                        "Download text",
                        data=text.encode("utf-8"),
                        file_name="sahaaya-document.txt",
                        mime="text/plain",
                    )
                st.caption(
                    "Verify legal, medical and financial details with the issuing office."
                )
        else:
            st.info("Add a page photo to run OCR.")

# ===========================================================================
# Schemes
# ===========================================================================
with scheme_tab:
    st.subheader("Disability schemes with citations")
    st.write(
        "Answers come from a versioned dataset. Eligibility is computed by rules, "
        "not generated by a language model. Every answer shows its source and the "
        "date it was last verified."
    )

    presets = [
        "What documents do I need for ADIP?",
        "What is the income limit for a free hearing aid under ADIP?",
        "How do I get a UDID card?",
        "What reservation does the RPwD Act give in jobs and education?",
    ]
    preset_cols = st.columns(len(presets))
    for index, preset in enumerate(presets):
        with preset_cols[index]:
            if st.button(preset, key=f"preset_{index}"):
                st.session_state["scheme_query"] = preset

    query = st.text_input(
        "Ask about a scheme",
        key="scheme_query",
        placeholder="e.g. ADIP income limit for a smart cane",
    )

    with st.expander("Check my eligibility (optional)"):
        profile_cols = st.columns(4)
        with profile_cols[0]:
            disability_percent = st.number_input(
                "Disability %", min_value=0, max_value=100, value=40, step=1
            )
        with profile_cols[1]:
            monthly_income = st.number_input(
                "Monthly family income (₹)", min_value=0, value=20000, step=500
            )
        with profile_cols[2]:
            has_udid = st.checkbox("I have a UDID card", value=False)
        with profile_cols[3]:
            has_aadhaar = st.checkbox("I have Aadhaar", value=True)
        use_profile = st.checkbox("Use these details in the eligibility check", value=False)

    if st.button("Search schemes", type="primary") and query:
        profile = (
            Profile(
                disability_percent=float(disability_percent),
                monthly_income_inr=float(monthly_income),
                has_udid=has_udid,
                has_aadhaar=has_aadhaar,
            )
            if use_profile
            else None
        )
        result = schemes.answer(query, profile=profile)
        st.markdown(result["answer"])

        if result["citations"]:
            citations = "<br>".join(
                f'<b>{item["name"]}</b> — <a href="{item["source_url"]}">{item["source_url"]}</a>'
                f' (verified {item["last_verified"]})'
                for item in result["citations"]
            )
            st.markdown(f'<div class="sd-cite">{citations}</div>', unsafe_allow_html=True)

        if st.button("🔊 Read answer aloud", key="speak_scheme"):
            audio = rag.text_to_speech_audio(result["answer"], language)
            if audio:
                st.audio(audio, format="audio/mp3")
            else:
                st.warning("Speech is unavailable (gTTS is not installed).")

    st.caption(
        f"Dataset version {schemes.dataset.get('dataset_version', 'unknown')} · "
        f"records {len(schemes.schemes)} · dataset verified "
        f"{schemes.dataset.get('last_verified', 'unknown')}"
    )

# ===========================================================================
# Out-of-scope archive
# ===========================================================================
with archive_tab:
    st.subheader("Modules outside the blind/low-vision v1 scope")
    st.write(
        "These modules are kept because they existed in the original project. They "
        "are prototypes for different user groups and are not part of the Sahaaya "
        "Drishti v1 release."
    )

    archive_choice = st.radio(
        "Choose a prototype",
        ["Classroom reader", "ISL practice", "AAC phrase board"],
        horizontal=True,
    )

    if archive_choice == "Classroom reader":
        title = st.selectbox("Lesson", classroom.get_lesson_titles())
        lesson = classroom.get_lesson(title)
        worksheet = st.text_area("Worksheet text", value=lesson["text"], height=150)
        st.caption(f"Simplified summary: {lesson['simplified']}")

        speed = st.slider("Speech speed factor", 0.5, 1.5, 1.0, 0.1)
        if st.button("🔊 Read worksheet", key="speak_worksheet"):
            audio = rag.text_to_speech_audio(worksheet, language, speed=speed)
            if audio:
                st.audio(audio, format="audio/mp3")
            else:
                st.warning("Speech is unavailable (gTTS is not installed).")

        st.markdown("---")
        st.markdown("#### Comprehension check")
        st.caption("Feedback appears only after you press Check.")
        for index, question in enumerate(lesson["questions"]):
            st.write(f"**Q{index + 1}. {question['q']}**")
            pick = st.radio(
                "Your answer",
                question["options"],
                index=None,
                key=f"cls_{title}_{index}",
                label_visibility="collapsed",
            )
            submitted_key = f"cls_submitted_{title}_{index}"
            if st.button("Check", key=f"cls_check_{title}_{index}"):
                st.session_state[submitted_key] = pick
            if submitted_key in st.session_state:
                answer = st.session_state[submitted_key]
                if answer is None:
                    st.info("Choose an option first.")
                elif answer == question["correct"]:
                    st.success(question["feedback"])
                else:
                    st.error(f"Not correct. {question['feedback']}")

    elif archive_choice == "ISL practice":
        category = st.selectbox("Category", isl.get_categories())
        for sign in isl.get_signs_by_category(category):
            with st.expander(f"{sign['icon']} {sign['name']}"):
                st.write(sign["instructions"])

        st.markdown("---")
        if "isl_quiz" not in st.session_state:
            st.session_state["isl_quiz"] = isl.generate_quiz_question()
        if st.button("New question", key="new_isl_question"):
            st.session_state["isl_quiz"] = isl.generate_quiz_question()
            st.session_state.pop("isl_answer", None)

        quiz = st.session_state["isl_quiz"]
        st.write(f"**{quiz['question']}**")
        choice = st.radio(
            "Your answer",
            [option["name"] for option in quiz["options"]],
            index=None,
            key=f"isl_choice_{quiz['correct_id']}",
        )
        if st.button("Check answer", key="check_isl"):
            if choice is None:
                st.info("Choose an option first.")
            elif choice == quiz["target"]["name"]:
                st.success("Correct.")
            else:
                st.error(f"Not correct. {quiz['explanation']}")

    else:
        st.caption(
            "The AAC board is translated into English, Hindi, Tamil, Telugu and "
            "Kannada only. Other languages are not offered here, because the "
            "previous version silently showed Hindi."
        )
        situation = st.selectbox("Situation", aac.get_situations())
        phrases = aac.get_phrases(situation)
        labels = [aac.get_translated_text(phrase, "en") for phrase in phrases]
        selected_index = st.selectbox(
            "Phrase", range(len(labels)), format_func=lambda index: labels[index]
        )
        phrase = phrases[selected_index]
        translated = aac.get_translation(phrase, language)
        if not translated["supported"]:
            st.warning(
                f"This phrase is not translated into {translated['fallback_from']}. "
                f"Showing {translated['language_name']} instead."
            )
        st.markdown(
            f"<div style='background:#fef3c7;border:2px solid #b45309;padding:20px;"
            f"border-radius:10px;font-size:1.4rem;text-align:center'>"
            f"{translated['text']}</div>",
            unsafe_allow_html=True,
        )
        if st.button("🔊 Speak phrase", key="speak_aac"):
            audio = rag.text_to_speech_audio(translated["text"], language)
            if audio:
                st.audio(audio, format="audio/mp3")
            else:
                st.warning("Speech is unavailable (gTTS is not installed).")

# ===========================================================================
# Safety and status
# ===========================================================================
with safety_tab:
    st.subheader("Emergency")
    st.write("A phone call is the only reliable emergency action. Location is not attached automatically.")
    st.link_button("📞 Call 112", "tel:112")
    st.markdown(
        "[Send a WhatsApp message](https://wa.me/?text=EMERGENCY%3A%20I%20need%20assistance.) "
        "— then attach your live location inside WhatsApp. This prototype does not "
        "read your GPS."
    )

    st.markdown("---")
    st.subheader("What this build does not do")
    st.markdown(
        "- It does **not** detect counterfeit notes.\n"
        "- It does **not** say a walking path is clear.\n"
        "- It does **not** estimate distance in metres.\n"
        "- It does **not** broadcast an SOS or a location.\n"
        "- It does **not** run in real time; Streamlit is a still-frame demo.\n"
        "- It does **not** support nine languages everywhere."
    )

    st.subheader("Data status")
    st.markdown(
        f"- Scheme dataset: `{schemes.dataset_path}` · "
        f"{len(schemes.schemes)} records · verified "
        f"{schemes.dataset.get('last_verified', 'unknown')}.\n"
        f"- Currency model: "
        f"{'loaded' if currency.model_available else 'not installed'}.\n"
        "- Demographics file: see the corrected notes in "
        "`knowledge_base/demographics_data.json`."
    )

    st.subheader("Where the real app lives")
    st.markdown(
        "- `android/` — Kotlin client (CameraX, TFLite, ML Kit, TalkBack, haptics).\n"
        "- `ml/currency/` — training, calibration, export and evaluation.\n"
        "- `ml/rag/` — retrieval evaluation harness.\n"
        "- `backend/` — read-only scheme update API.\n"
        "- `docs/CLAIMS_MATRIX.md` — every public claim and its evidence."
    )
