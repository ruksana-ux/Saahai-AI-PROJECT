"""
Sahaaya AI (सहाय) — Accessibility Without Barriers
100% Pure Python Assistive Platform for India.
Integrated with LLM & RAG Copilot, Computer Vision, Currency Classifier,
ISL Education Studio, Indian AAC Board, and Classroom Assessment Engine.
"""

import streamlit as st
from PIL import Image

# 100% Pure Python Engine Imports
from rag_engine import SahaayaRAGEngine
from cv_engine import SahaayaVisionEngine
from currency_engine import SahaayaCurrencyEngine
from isl_engine import SahaayaISLEngine
from aac_engine import SahaayaAACEngine
from classroom_engine import SahaayaClassroomEngine

# Streamlit Page Configuration
st.set_page_config(
    page_title="Sahaaya AI (सहाय) — 100% Python Assistive Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Python Engines in Streamlit Cache
@st.cache_resource
def load_all_engines():
    return {
        "rag": SahaayaRAGEngine(kb_dir="knowledge_base"),
        "vision": SahaayaVisionEngine(),
        "currency": SahaayaCurrencyEngine(),
        "isl": SahaayaISLEngine(),
        "aac": SahaayaAACEngine(),
        "classroom": SahaayaClassroomEngine()
    }

engines = load_all_engines()
rag = engines["rag"]
vision = engines["vision"]
currency = engines["currency"]
isl = engines["isl"]
aac = engines["aac"]
classroom = engines["classroom"]

# --- ACCESSIBILITY CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", sans-serif;
    }
    .brand-header {
        background: linear-gradient(135deg, #00796B 0%, #004D40 100%);
        color: white;
        padding: 22px 26px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
    }
    .brand-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .brand-badge {
        background: #FFB300;
        color: #000;
        padding: 4px 14px;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 900;
    }
    .citation-box {
        background: #F1F5F9;
        border-left: 4px solid #00796B;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.9rem;
        margin-top: 12px;
    }
    .flip-card-view {
        background: #FEF3C7;
        border: 3px solid #D97706;
        padding: 24px;
        border-radius: 12px;
        text-align: center;
        transform: rotate(180deg);
        margin: 16px 0;
    }
    .hazard-box-danger {
        background: #FEE2E2;
        border: 2px solid #DC2626;
        padding: 14px;
        border-radius: 8px;
        color: #991B1B;
    }
    .hazard-box-safe {
        background: #DCFCE7;
        border: 2px solid #16A34A;
        padding: 14px;
        border-radius: 8px;
        color: #166534;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://images.openai.com/static-rsc-4/hLQKrAZLCbvXvuBaUe6o1lNEGmiO0_cviiQoTMN_aZsbxoJYmpePg7NQA0qYqw1AOW88E5l_C3U0XzLR2ATiMlFBUkxWic56hpf3PZIq5amdva7zOG8aWuJpH9Q0N_bGhZlaBJOqPsJqrXxj9LAkpLxnF4WCdieLkkefM1i4lXUt4YVa8gn0t403oaxNQHK5?purpose=inline", use_container_width=True)
    st.title("⚙️ Assistive Controls")

    target_lang = st.selectbox(
        "🌐 Voice & Interface Language",
        ["Hindi", "English", "Tamil", "Telugu", "Kannada", "Bengali", "Malayalam", "Marathi", "Gujarati"],
        index=0
    )

    disability_profile = st.radio(
        "👤 Adaptive Disability Profile",
        ["🌟 All Tools Mode", "👁️ Visually Impaired", "🧏 Deaf & Hard-of-Hearing", "🗣️ Nonspeaking / AAC", "🦯 Deafblind Mode"],
        index=0
    )

    st.markdown("---")
    st.subheader("🤖 LLM & RAG Configuration")

    gemini_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    openai_key = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""

    user_gemini_key = st.text_input("Google Gemini API Key (Optional)", value=gemini_key, type="password")
    user_openai_key = st.text_input("OpenAI API Key (Optional)", value=openai_key, type="password")

    if user_gemini_key:
        st.success("⚡ Gemini 1.5 Flash Active")
    elif user_openai_key:
        st.success("⚡ OpenAI GPT-4o-mini Active")
    else:
        st.info("ℹ️ Built-in Offline Neural RAG Active (No Key Required)")

    st.markdown("---")
    st.subheader("🇮🇳 Key National Statistics")
    st.markdown("""
    - **Total Population**: ~1.48 Billion (Rank 1)
    - **Disability Rate**: **2.21%** (~2.68 Cr citizens)
    - **Unmet Tech Need**: **70%** (WHO-UNICEF)
    - **Out-of-Pocket Cost**: **67.4%**
    - **Highest Burden State**: **Uttar Pradesh (15.5%)**
    - **National Helpline**: **1800-180-5129 (ALIMCO)**
    """)

# --- MAIN BRAND HEADER ---
st.markdown("""
<div class="brand-header">
    <div class="brand-title">
        <span>Sahaaya AI</span>
        <span class="brand-badge">सहाय</span>
    </div>
    <p style="margin: 6px 0 0 0; opacity: 0.94; font-size: 1.05rem;">
        Accessibility Without Barriers • 100% Pure Python Assistive Technology Platform for India
    </p>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tabs = st.tabs([
    "🧠 LLM & RAG Copilot",
    "💵 Currency & Coin AI",
    "🏫 Classroom & OCR",
    "🚸 Street Hazard Vision",
    "🤟 ISL Education Studio",
    "🗣️ Indian AAC Board",
    "📊 Demographics & Schemes"
])

# ==============================================================================
# TAB 1: LLM & RAG ASSISTIVE COPILOT
# ==============================================================================
with tabs[0]:
    st.subheader("🧠 Sahaaya LLM & RAG Assistive Copilot")
    st.markdown(
        "Ask questions about **government welfare schemes (ADIP, UDID, RPwD Act 2016)**, "
        "medical accommodations, or technology gap fixes. Grounded in verified Indian data."
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("📋 How do I get free hearing aids / smart canes under ADIP Scheme?"):
            st.session_state["query_input"] = "How do I apply for free hearing aids or smart canes under the ADIP Scheme?"
        if st.button("⚖️ What are the key rights under RPwD Act 2016 for education and jobs?"):
            st.session_state["query_input"] = "What are the legal reservations and rights under the Rights of Persons with Disabilities Act 2016?"
    with col_p2:
        if st.button("🔍 Why does RBI MANI app fail on Indian street currency?"):
            st.session_state["query_input"] = "What are the critical drawbacks of RBI MANI app and how does Sahaaya AI solve them?"
        if st.button("🛡️ How to verify counterfeit ₹500 notes using tactile marks?"):
            st.session_state["query_input"] = "How can a visually impaired person detect counterfeit ₹500 notes using tactile marks?"

    query = st.text_input(
        "Ask a question in your preferred language:",
        value=st.session_state.get("query_input", ""),
        placeholder="e.g. How to get travel concessions using UDID card?"
    )

    if st.button("🚀 Ask Sahaaya AI", type="primary") and query:
        with st.spinner("Retrieving verified Indian knowledge and synthesizing response..."):
            rag_res = rag.generate_answer(
                query=query,
                lang=target_lang,
                gemini_api_key=user_gemini_key or gemini_key,
                openai_api_key=user_openai_key or openai_key
            )

            st.markdown(rag_res["answer"])

            st.markdown(f"""
            <div class="citation-box">
                <b>📚 Grounded Sources Cited:</b> {', '.join(rag_res['sources'])}<br>
                <b>🤖 Synthesis Engine:</b> {rag_res['engine']}
            </div>
            """, unsafe_allow_html=True)

            audio_fp = rag.text_to_speech_audio(rag_res["answer"], target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

# ==============================================================================
# TAB 2: RUPEE CURRENCY & COIN AI IDENTIFIER
# ==============================================================================
with tabs[1]:
    st.subheader("💵 Indian Rupee Banknote & Coin AI Identifier (Pure Python)")
    st.markdown(
        "Solves the RBI MANI app shortcomings by identifying **banknotes AND coins** "
        "(including the 12-sided ₹20 dodecagon coin) with anti-counterfeit verification checklists."
    )

    curr_col1, curr_col2 = st.columns([1, 1])

    with curr_col1:
        cam_image = st.camera_input("📸 Point camera at Indian Banknote or Coin")
        uploaded_image = st.file_uploader("Or upload currency photo", type=["jpg", "jpeg", "png"])
        target_img = cam_image or uploaded_image

    with curr_col2:
        if target_img:
            img = Image.open(target_img)
            st.image(img, caption="Viewfinder Image", use_container_width=True)

            res = currency.classify_image(img)

            st.success(f"### Detected: {res['denomination']} ({res['confidence']}% confidence)")
            st.info(f"**Series & Theme**: {res['series']} • {res['color']} • {res['motif']}")
            st.warning(f"**📳 Tactile Haptic Vibration Pattern**: {res['haptic_pattern']}")
            st.write(f"**🔍 Key Tactile Mark**: {res['tactile_mark']}")

            st.markdown("#### 🛡️ Anti-Counterfeit Verification Checklist:")
            for check in res["security_checklist"]:
                st.markdown(f"- ✅ {check}")

            audio_fp = rag.text_to_speech_audio(f"Identified {res['denomination']}. {res['color']}. Verify tactile bleed lines.", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

        else:
            st.info("💡 Position currency in camera view above, or select a test denomination below:")
            pick_curr = st.selectbox(
                "Manual Denomination Inspector:",
                ["500", "200", "100", "50", "20", "10"],
                format_func=lambda x: currency.CURRENCY_SPECS[x]["name"]
            )
            spec = currency.CURRENCY_SPECS[pick_curr]
            st.write(f"**Denomination**: {spec['name']}")
            st.write(f"**Series**: {spec['series']} • {spec['color']} • {spec['motif']}")
            st.write(f"**Tactile Mark**: {spec['tactile_mark']}")
            for check in spec["security_checklist"]:
                st.write(f"- ✅ {check}")

# ==============================================================================
# TAB 3: ACCESSIBLE CLASSROOM & OCR
# ==============================================================================
with tabs[2]:
    st.subheader("🏫 Accessible Indian Classroom & OCR Engine (Pure Python)")
    st.markdown(
        "Scan worksheets, textbook paragraphs, or school circulars. "
        "Listen to spoken read-alouds, simplified summaries, and test comprehension with auto-generated quizzes."
    )

    cls_col1, cls_col2 = st.columns([1, 1])

    with cls_col1:
        selected_title = st.selectbox("📑 Select Preloaded Indian Lesson:", classroom.get_lesson_titles())
        lesson_data = classroom.get_lesson(selected_title)

        worksheet_text = st.text_area(
            "Worksheet Text Content:",
            value=lesson_data["text"],
            height=160
        )

        st.markdown(f"**💡 Simplified Student Summary**: {lesson_data['simplified']}")
        st.write(f"**🤟 Related ISL Concepts**: {', '.join(lesson_data['related_isl_signs'])}")

    with cls_col2:
        speed = st.slider("🔊 Readout Speed", 0.5, 1.5, 1.0, 0.1)
        if st.button("🔊 Read Worksheet Aloud"):
            audio_fp = rag.text_to_speech_audio(worksheet_text, target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

        st.markdown("---")
        st.subheader("📝 Automated Comprehension Quiz")
        for i, q in enumerate(lesson_data["questions"]):
            st.write(f"**Q{i+1}: {q['q']}**")
            pick = st.radio(f"Select answer for Q{i+1}:", q["options"], key=f"q_{selected_title}_{i}")
            if pick == q["correct"]:
                st.success(f"✅ {q['feedback']}")

# ==============================================================================
# TAB 4: STREET HAZARD COMPUTER VISION
# ==============================================================================
with tabs[3]:
    st.subheader("🚸 Street Hazard Computer Vision & Mobility (Pure Python)")
    st.markdown(
        "Supplements white canes and mobility aids by analyzing camera snapshots for "
        "**open potholes, storm drains (nalas), low hanging overhead wires, and obstacles**."
    )

    v_col1, v_col2 = st.columns([1, 1])

    with v_col1:
        hazard_cam = st.camera_input("📸 Capture Street Walking Path")
        hazard_file = st.file_uploader("Or upload street scene photo", type=["jpg", "jpeg", "png"], key="hazard_upload")
        active_hazard_img = hazard_cam or hazard_file

    with v_col2:
        if active_hazard_img:
            pil_img = Image.open(active_hazard_img)
            analysis = vision.analyze_street_image(pil_img)

            st.image(analysis["annotated_image"], caption="Annotated Hazard Inspection", use_container_width=True)

            if analysis["is_danger"]:
                st.markdown(f"""
                <div class="hazard-box-danger">
                    <h3>{analysis['primary_status']}</h3>
                    <p><b>Recommended Action:</b> {analysis['primary_action']}</p>
                    <p><b>Tactile Haptic Pattern:</b> {analysis['primary_haptic']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="hazard-box-safe">
                    <h3>{analysis['primary_status']}</h3>
                    <p>{analysis['primary_action']}</p>
                </div>
                """, unsafe_allow_html=True)

            audio_fp = rag.text_to_speech_audio(f"{analysis['primary_status']}. {analysis['primary_action']}", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
        else:
            st.info("💡 Position camera toward your walking path or upload a test street image.")

    st.markdown("---")
    st.subheader("🆘 Emergency SOS Beacon & Geolocation Broadcast")
    sos_col1, sos_col2 = st.columns(2)
    with sos_col1:
        if st.button("🚨 TRIGGER EMERGENCY SOS BEACON", type="primary"):
            st.error("🚨 EMERGENCY SOS BROADCAST ACTIVATED!")
            st.write("Vibrating Morse SOS pattern: `••• --- •••`")
            st.audio(rag.text_to_speech_audio("Emergency SOS beacon activated! Assisting person nearby.", "en"), format="audio/mp3")
    with sos_col2:
        maps_link = "https://maps.google.com/?q=28.6139,77.2090"
        wa_url = f"https://wa.me/?text=EMERGENCY%3A+I+need+assistance.+My+current+location+is+{maps_link}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="padding:10px 20px; background:#25D366; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📲 Send SOS on WhatsApp</button></a>', unsafe_allow_html=True)

# ==============================================================================
# TAB 5: INDIAN SIGN LANGUAGE STUDIO
# ==============================================================================
with tabs[4]:
    st.subheader("🤟 Indian Sign Language (ISL) Education Studio (Pure Python)")
    st.markdown(
        "Standardized curriculum aligned with **ISLRTC & NCERT Channel 31** guidelines. "
        "Learn essential gestures for Indian classrooms, healthcare, transit, and emergencies."
    )

    selected_cat = st.selectbox("Select ISL Category:", isl.get_categories())
    signs_list = isl.get_signs_by_category(selected_cat)

    cols = st.columns(len(signs_list))
    for idx, item in enumerate(signs_list):
        with cols[idx]:
            st.markdown(f"""
            <div style="background:#E6F0ED; padding:16px; border-radius:10px; border:2px solid #00796B; text-align:center; min-height:220px;">
                <div style="font-size:2.6rem;">{item['icon']}</div>
                <h4 style="margin:8px 0; color:#004D40;">{item['name']}</h4>
                <p style="font-size:0.85rem; color:#48656E;">{item['instructions']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔊 Listen", key=f"isl_speak_{idx}"):
                audio_fp = rag.text_to_speech_audio(f"{item['name']}. {item['instructions']}", target_lang)
                if audio_fp:
                    st.audio(audio_fp, format="audio/mp3")

    st.markdown("---")
    st.subheader("🎯 Test Your Knowledge: Randomized ISL Practice Quiz")
    if st.button("🎲 Generate New Question"):
        st.session_state["isl_quiz"] = isl.generate_quiz_question()

    active_quiz = st.session_state.get("isl_quiz", isl.generate_quiz_question())
    st.write(f"### {active_quiz['question']}")
    quiz_cols = st.columns(len(active_quiz["options"]))
    for i, opt in enumerate(active_quiz["options"]):
        with quiz_cols[i]:
            if st.button(f"{opt['icon']} {opt['name']}", key=f"quiz_opt_{i}"):
                if opt["id"] == active_quiz["correct_id"]:
                    st.success("🎉 Correct Answer! Excellent.")
                else:
                    st.error(f"❌ Not quite. {active_quiz['explanation']}")

# ==============================================================================
# TAB 6: AAC INDIAN SITUATION BOARD
# ==============================================================================
with tabs[5]:
    st.subheader("🗣️ Augmentative & Alternative Communication (AAC) Board (Pure Python)")
    st.markdown("Rapid dialogue presets for Indian clinics, auto-rickshaws, ration/kirana shops, and government offices.")

    chosen_sit = st.selectbox("Select Situation:", aac.get_situations())
    phrases = aac.get_phrases(chosen_sit)

    phrase_options = [aac.get_translated_text(p, target_lang) for p in phrases]
    selected_dialogue = st.selectbox("Select Phrase to Display & Speak:", phrase_options)

    st.markdown("### 🔄 180° Tabletop Flip View (Show across desk/counter):")
    st.markdown(f"""
    <div class="flip-card-view">
        <h2 style="color:#B45309; margin:0;">{selected_dialogue}</h2>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔊 Speak Phrase Out Loud", type="primary"):
        audio_fp = rag.text_to_speech_audio(selected_dialogue, target_lang)
        if audio_fp:
            st.audio(audio_fp, format="audio/mp3")

# ==============================================================================
# TAB 7: INDIA DEMOGRAPHICS & SCHEMES DASHBOARD
# ==============================================================================
with tabs[6]:
    st.subheader("📊 India Disability Demographics & Welfare Schemes Hub (Pure Python)")
    st.markdown("Verified statistical landscape compiled from Census of India, NSS, LASI, and WHO-UNICEF reports.")

    metric_c1, metric_c2, metric_c3, metric_c4 = st.columns(4)
    with metric_c1:
        st.metric("Total Population", "1.48 Billion", "Global Rank #1")
    with metric_c2:
        st.metric("Disability Rate", "2.21%", "~2.68 Cr citizens")
    with metric_c3:
        st.metric("Unmet Tech Need", "70%", "WHO-UNICEF GReAT")
    with metric_c4:
        st.metric("Out-of-Pocket Cost", "67.4%", "Paid by Families")

    st.markdown("---")
    st.subheader("Top Indian States by Disability Population Share")

    state_data = {
        "Uttar Pradesh": {"share": "15.5% - 16.5%", "blind": "~7.63 Lakh", "notes": "Steep affordability barrier; rural families lack digital tools and rely on mechanical slates."},
        "Maharashtra": {"share": "11.05%", "blind": "High", "notes": "Significant adult workforce disability burden; rural Marathwada and Vidarbha face training gaps."},
        "Bihar": {"share": "8.69%", "blind": "High", "notes": "Multidimensional poverty clusters; digital hearing aids (₹20k+) and cochlear implants are unaffordable."},
        "Andhra Pradesh": {"share": "8.45%", "blind": "High", "notes": "High rural density; lack of localized Telugu assistive tools."},
        "West Bengal": {"share": "7.52%", "blind": "High", "notes": "High elderly sensory decline (presbycusis and cataracts); urgent need for Bengali audio tools."}
    }

    for s_name, s_info in state_data.items():
        st.markdown(f"**📍 {s_name}** — National Share: **{s_info['share']}** | Context: {s_info['notes']}")

    st.markdown("---")
    st.subheader("🏛️ Central Government Welfare Schemes & Helplines")
    st.markdown("""
    - **ADIP Scheme**: 100% free or subsidized smart canes, hearing aids, and wheelchairs for families with monthly income under ₹15,000.  
      🔗 [ADIP Portal](https://adip.depwd.gov.in/) | Toll-Free ALIMCO Helpline: **1800-180-5129**
    - **UDID Card (Swavlamban)**: Universal disability card enabling up to 75% concessions in Indian Railways.  
      🔗 [Swavlamban Portal](https://www.swavlambancard.gov.in/)
    - **RPwD Act 2016**: 4% government job reservation and 5% higher education reservation.
    """)
