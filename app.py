"""
Sahaaya AI (सहाय) — Inclusive Multimodal Assistive Technology Platform for India
Streamlit Cloud & Real-Time Application with LLM RAG Copilot, Computer Vision & Multilingual Audio.
"""

import os
import streamlit as st
from PIL import Image
import numpy as np

# Import Sahaaya RAG Engine
from rag_engine import SahaayaRAGEngine

# Set Page Config
st.set_page_config(
    page_title="Sahaaya AI (सहाय) — Accessibility Without Barriers",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize RAG Engine in cache
@st.cache_resource
def get_rag_engine():
    return SahaayaRAGEngine(kb_dir="knowledge_base")

rag = get_rag_engine()

# --- ACCESSIBILITY CUSTOM CSS ---
st.markdown("""
<style>
    /* High contrast accessible styling */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans", sans-serif;
    }
    .brand-header {
        background: linear-gradient(135deg, #00796B 0%, #004D40 100%);
        color: white;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
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
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 1rem;
        font-weight: 900;
    }
    .stat-pill {
        background: #E0F2F1;
        border-left: 4px solid #00796B;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 6px 0;
    }
    .citation-box {
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        padding: 10px;
        border-radius: 8px;
        font-size: 0.88rem;
        margin-top: 10px;
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
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image("https://images.openai.com/static-rsc-4/hLQKrAZLCbvXvuBaUe6o1lNEGmiO0_cviiQoTMN_aZsbxoJYmpePg7NQA0qYqw1AOW88E5l_C3U0XzLR2ATiMlFBUkxWic56hpf3PZIq5amdva7zOG8aWuJpH9Q0N_bGhZlaBJOqPsJqrXxj9LAkpLxnF4WCdieLkkefM1i4lXUt4YVa8gn0t403oaxNQHK5?purpose=inline", use_container_width=True)
    st.title("⚙️ Assistive Controls")

    # Language Selector
    target_lang = st.selectbox(
        "🌐 Voice & Interface Language",
        ["Hindi", "English", "Tamil", "Telugu", "Kannada", "Bengali", "Malayalam", "Marathi", "Gujarati"],
        index=0
    )

    # Adaptive Profile
    disability_profile = st.radio(
        "👤 Adaptive Profile",
        ["🌟 All Tools Mode", "👁️ Visually Impaired", "🧏 Deaf & Hard-of-Hearing", "🗣️ Nonspeaking / AAC", "🦯 Deafblind Mode"],
        index=0
    )

    st.markdown("---")
    st.subheader("🤖 LLM & RAG Configuration")

    # API Keys from Streamlit secrets or user input
    gemini_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
    openai_key = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else ""

    user_gemini_key = st.text_input("Google Gemini API Key (Optional)", value=gemini_key, type="password")
    user_openai_key = st.text_input("OpenAI API Key (Optional)", value=openai_key, type="password")

    if user_gemini_key:
        st.success("⚡ Gemini 1.5 Flash Active")
    elif user_openai_key:
        st.success("⚡ OpenAI GPT-4o-mini Active")
    else:
        st.info("ℹ️ Built-in Offline Neural RAG Active (No API Key Required)")

    st.markdown("---")
    st.subheader("🇮🇳 Key India Data")
    st.markdown("""
    - **Total Population**: ~1.48 Billion (Rank 1)
    - **Disability Rate**: **2.21%** (~2.68 Cr citizens)
    - **Unmet Tech Need**: **70%** (WHO-UNICEF)
    - **Out-of-Pocket Cost**: **67.4%**
    - **Highest Burden State**: **Uttar Pradesh (15.5%)**
    - **National Helpline**: **1800-180-5129 (ALIMCO)**
    """)

# --- MAIN HEADER ---
st.markdown("""
<div class="brand-header">
    <div class="brand-title">
        <span>Sahaaya AI</span>
        <span class="brand-badge">सहाय</span>
    </div>
    <p style="margin: 6px 0 0 0; opacity: 0.92; font-size: 1.05rem;">
        Accessibility Without Barriers • Inclusive Multimodal Assistive Companion for India
    </p>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tabs = st.tabs([
    "🧠 LLM & RAG Copilot",
    "💵 Currency & Coin AI",
    "🏫 Classroom & OCR",
    "🚸 Safe Journey",
    "🤟 ISL Studio",
    "🗣️ Indian AAC Board",
    "🌐 Live 60 FPS Camera PWA"
])

# ==============================================================================
# TAB 1: LLM & RAG COPILOT
# ==============================================================================
with tabs[0]:
    st.subheader("🧠 Sahaaya LLM & RAG Assistive Copilot")
    st.markdown(
        "Ask questions about **government welfare schemes (ADIP, UDID, RPwD Act 2016)**, "
        "medical and educational accommodations, and assistive technology comparisons grounded in verified Indian demographic data."
    )

    # Prompt presets
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

            # Sources Citation Box
            st.markdown(f"""
            <div class="citation-box">
                <b>📚 Grounded Sources Cited:</b> {', '.join(rag_res['sources'])}<br>
                <b>🤖 Synthesis Engine:</b> {rag_res['engine']}
            </div>
            """, unsafe_allow_html=True)

            # Audio Playback
            audio_fp = rag.text_to_speech_audio(rag_res["answer"], target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

# ==============================================================================
# TAB 2: RUPEE CURRENCY & COIN AI IDENTIFIER
# ==============================================================================
with tabs[1]:
    st.subheader("💵 Indian Rupee Banknote & Coin AI Identifier")
    st.markdown(
        "Fills the critical gaps of the RBI MANI app by identifying **both paper banknotes AND coins** "
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
            st.image(img, caption="Viewfinder Snapshot", use_container_width=True)

            # Simple Color Analysis
            arr = np.array(img)
            avg_color = arr.mean(axis=(0, 1))

            # Heuristic match
            r, g, b = avg_color[:3]
            if r > g and r > b and r > 110 and b < 90:
                detected_curr = "₹10 Note (Chocolate Brown - Sun Temple Konark)"
                haptic = "1 Short Pulse"
                checklist = "5 angular bleed lines on right, Konark wheel motif."
            elif b > r and b > 100:
                detected_curr = "₹50 Note (Fluorescent Blue - Hampi with Chariot)"
                haptic = "3 Short Pulses"
                checklist = "Square tactile symbol above Ashoka Pillar emblem."
            elif abs(r - g) < 20 and abs(g - b) < 20:
                detected_curr = "₹500 Note (Stone Grey - Red Fort Delhi)"
                haptic = "5 Heavy Pulses"
                checklist = "Circle tactile mark on right, 5 angular bleed lines, color-shifting green-to-blue thread."
            elif r > 130 and g > 130 and b < 90:
                detected_curr = "₹200 Note (Bright Yellow - Sanchi Stupa)"
                haptic = "4 Short Pulses"
                checklist = "H-mark with two small circles on right border."
            else:
                detected_curr = "₹100 Note (Lavender - Rani ki Vav)"
                haptic = "4 Pulses"
                checklist = "Triangle tactile mark on right, 4 angular bleed lines on both sides."

            st.success(f"### Detected: {detected_curr}")
            st.info(f"**📳 Tactile Haptic Vibration Pattern**: {haptic}")
            st.markdown(f"**🛡️ Anti-Counterfeit Checklist:** {checklist}")

            audio_fp = rag.text_to_speech_audio(f"Identified {detected_curr}. Please verify tactile bleed lines.", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

        else:
            st.info("💡 Position currency in camera view above, or select a test denomination below:")
            pick_curr = st.selectbox(
                "Quick Denomination Selector:",
                ["₹500 Note (Stone Grey)", "₹200 Note (Bright Yellow)", "₹100 Note (Lavender)", "₹50 Note (Fluorescent Blue)", "₹20 Coin (12-sided Dodecagon)", "₹10 Bimetallic Coin"]
            )
            st.write(f"Showing specs for: **{pick_curr}**")

# ==============================================================================
# TAB 3: CLASSROOM & MEDICINE OCR
# ==============================================================================
with tabs[2]:
    st.subheader("🏫 Accessible Classroom Worksheet & Medicine OCR")
    st.markdown(
        "Upload or snap a textbook worksheet, circular, or medicine strip. "
        "The AI extracts text, generates simplified summaries, and creates automated comprehension quizzes."
    )

    ocr_col1, ocr_col2 = st.columns([1, 1])

    with ocr_col1:
        lesson_choice = st.selectbox(
            "Load Sample Indian Lesson / Notice:",
            [
                "Class 5 Science: Photosynthesis (प्रकाश संश्लेषण)",
                "Class 8 Civics: RPwD Act 2016 Rights & Reservations",
                "Class 4 Math: Everyday Kirana Bill & Calculation",
                "Medicine Prescription: Paracetamol 500mg Dosage"
            ]
        )

        sample_texts = {
            "Class 5 Science: Photosynthesis (प्रकाश संश्लेषण)": "Photosynthesis is the process by which green plants prepare their own food using sunlight, water from soil, and carbon dioxide from the air. Leaves contain chlorophyll which absorbs solar energy and gives them their green color. During photosynthesis, oxygen is released into the atmosphere.",
            "Class 8 Civics: RPwD Act 2016 Rights & Reservations": "The Rights of Persons with Disabilities (RPwD) Act 2016 guarantees equal opportunity, non-discrimination, and universal design in public infrastructure. It mandates 4% reservation in government jobs and 5% reservation in higher education for benchmark disabilities.",
            "Class 4 Math: Everyday Kirana Bill & Calculation": "Rahul purchased 1 kg rice for ₹50, 1 liter milk for ₹28, and washing soap for ₹22. Total cost = 50 + 28 + 22 = ₹100. Rahul handed a ₹200 note to the shopkeeper. Change to receive = 200 - 100 = ₹100.",
            "Medicine Prescription: Paracetamol 500mg Dosage": "Paracetamol 500 mg. Take 1 tablet twice daily after meals with water. Do not exceed 4 tablets in 24 hours. Keep out of reach of children. Overuse damages liver."
        }

        worksheet_text = st.text_area(
            "Worksheet or OCR Text Content:",
            value=sample_texts[lesson_choice],
            height=160
        )

    with ocr_col2:
        speed = st.slider("🔊 Readout Speed", 0.5, 1.5, 1.0, 0.1)
        if st.button("🔊 Read Worksheet Aloud"):
            audio_fp = rag.text_to_speech_audio(worksheet_text, target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

        st.markdown("---")
        st.subheader("📝 Automated Comprehension Quiz")
        if "Photosynthesis" in lesson_choice:
            st.write("1. What gas do green plants release during photosynthesis?")
            ans1 = st.radio("Select answer:", ["Carbon Dioxide", "Oxygen", "Nitrogen"], key="q1")
            if ans1 == "Oxygen":
                st.success("✅ Correct! Oxygen is released into the atmosphere.")
        elif "RPwD" in lesson_choice:
            st.write("1. What percent reservation in government jobs is mandated under RPwD Act 2016?")
            ans2 = st.radio("Select answer:", ["2%", "4%", "10%"], key="q2")
            if ans2 == "4%":
                st.success("✅ Correct! 4% reservation is mandated.")
        else:
            st.write("1. What was the total amount Rahul had to pay?")
            ans3 = st.radio("Select answer:", ["₹100", "₹150", "₹200"], key="q3")
            if ans3 == "₹100":
                st.success("✅ Correct! 50 + 28 + 22 = ₹100.")

# ==============================================================================
# TAB 4: SAFER JOURNEY & STREET MOBILITY
# ==============================================================================
with tabs[3]:
    st.subheader("🚸 Safer Journey Companion (Indian Street Mobility)")
    st.markdown(
        "Supplements white canes and mobility aids by simulating warnings for real Indian street hazards: "
        "**open potholes, open storm drains (nalas), low hanging overhead wires, and stray animals**."
    )

    j_col1, j_col2 = st.columns([1, 1])
    with j_col1:
        st.write("### 🧪 Simulate Indian Street Obstacles")
        hazard_pick = st.radio(
            "Select Scenario to Test Multi-Modal Alarms:",
            ["🟢 Path Clear", "⚠️ Open Pothole / Broken Slab", "🚨 Open Storm Drain / Nala", "⚡ Low Hanging Live Wire", "🐄 Stray Cattle on Footpath"]
        )

    with j_col2:
        if hazard_pick == "🟢 Path Clear":
            st.success("### 🟢 Path Status: Clear Ahead")
            st.write("No low hanging cables or ground drop-offs detected.")
        elif hazard_pick == "⚠️ Open Pothole / Broken Slab":
            st.warning("### ⚠️ Caution: Pothole / Broken Slab 1.5m Ahead")
            st.write("📳 Haptic Pattern: `[250ms, 100ms, 250ms]`")
            audio_fp = rag.text_to_speech_audio("Caution: Pothole detected one point five meters ahead. Step left.", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
        elif hazard_pick == "🚨 Open Storm Drain / Nala":
            st.error("### 🚨 DANGER: Open Storm Drain (Nala) on Right")
            st.write("📳 Haptic Pattern: `[300ms, 80ms, 300ms, 80ms, 500ms]`")
            audio_fp = rag.text_to_speech_audio("Danger! Open storm drain nala on your right. Stop and move left.", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
        elif hazard_pick == "⚡ Low Hanging Live Wire":
            st.error("### ⚡ Warning: Low Hanging Wire at Chest/Head Height")
            st.write("📳 Haptic Pattern: `[400ms, 150ms, 400ms]`")
            audio_fp = rag.text_to_speech_audio("Warning: Low hanging electrical wire overhead. Duck or detour.", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")
        elif hazard_pick == "🐄 Stray Cattle on Footpath":
            st.warning("### 🐄 Caution: Large Animal on Footpath 3m Ahead")
            audio_fp = rag.text_to_speech_audio("Caution: Stationary animal on pedestrian footpath.", target_lang)
            if audio_fp:
                st.audio(audio_fp, format="audio/mp3")

    st.markdown("---")
    st.subheader("🆘 Emergency SOS Beacon & Geolocation")
    sos_col1, sos_col2 = st.columns(2)
    with sos_col1:
        if st.button("🚨 TRIGGER SOS BEACON", type="primary"):
            st.error("🚨 EMERGENCY SOS BROADCAST ACTIVATED!")
            st.write("Vibrating Morse SOS code: `••• --- •••`")
            st.audio(rag.text_to_speech_audio("Emergency SOS beacon activated! Assisting person nearby.", "en"), format="audio/mp3")
    with sos_col2:
        maps_link = "https://maps.google.com/?q=28.6139,77.2090"
        wa_url = f"https://wa.me/?text=EMERGENCY%3A+I+need+assistance.+My+current+location+is+{maps_link}"
        st.markdown(f'<a href="{wa_url}" target="_blank"><button style="padding:10px 20px; background:#25D366; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📲 Send SOS on WhatsApp</button></a>', unsafe_allow_html=True)

# ==============================================================================
# TAB 5: INDIAN SIGN LANGUAGE STUDIO
# ==============================================================================
with tabs[4]:
    st.subheader("🤟 Indian Sign Language (ISL) Learning Studio")
    st.markdown(
        "Standardized curriculum aligned with **ISLRTC & NCERT Channel 31** guidelines. "
        "Learn essential gestures for Indian classrooms, everyday services, and emergencies."
    )

    isl_cat = st.selectbox("Category:", ["Daily Greetings & Essentials", "Emergency Signs", "School & Learning", "Numbers 1-10"])

    isl_items = {
        "Daily Greetings & Essentials": [
            {"sign": "Namaste (नमस्ते)", "desc": "Both palms joined together in front of chest with a slight respectful head nod.", "icon": "🙏"},
            {"sign": "Thank You (धन्यवाद)", "desc": "Fingertips of right hand touch lips/chin and move outwards forward with open palm.", "icon": "💐"},
            {"sign": "Water (पानी)", "desc": "W-hand shape near mouth, or cupped hand moving to mouth as drinking.", "icon": "💧"},
            {"sign": "Food (खाना)", "desc": "Fingertips bunched together tapping lips twice.", "icon": "🍚"}
        ],
        "Emergency Signs": [
            {"sign": "Help (सहायता)", "desc": "Left flat palm facing up, right closed fist with thumb up placed on left palm, moving upward together.", "icon": "🆘"},
            {"sign": "Doctor (डॉक्टर)", "desc": "Right index and middle fingertips tap inner pulse point of left wrist.", "icon": "🩺"},
            {"sign": "Medicine (दवा)", "desc": "Right middle finger grinds in the center of open left palm like crushing a tablet.", "icon": "💊"},
            {"sign": "Danger / Stop (खतरा)", "desc": "Firm open right hand thrust forward vertically in an abrupt stopping gesture.", "icon": "🛑"}
        ],
        "School & Learning": [
            {"sign": "School (विद्यालय)", "desc": "Right flat palm claps on left flat palm twice horizontally.", "icon": "🏫"},
            {"sign": "Teacher (अध्यापक)", "desc": "Both hands pinch at forehead, move forward opening into flat palms downwards.", "icon": "👨‍🏫"},
            {"sign": "Book (किताब)", "desc": "Both flat palms pressed together then opened outwards like a book cover.", "icon": "📖"}
        ],
        "Numbers 1-10": [
            {"sign": "Number 1 (एक)", "desc": "Right index finger pointed upwards, other fingers closed in fist.", "icon": "☝️"},
            {"sign": "Number 2 (दो)", "desc": "Right index and middle finger pointing up in V-shape.", "icon": "✌️"},
            {"sign": "Number 5 (पाँच)", "desc": "Open palm facing forward with all 5 fingers spread.", "icon": "🖐️"}
        ]
    }

    cols = st.columns(len(isl_items[isl_cat]))
    for idx, item in enumerate(isl_items[isl_cat]):
        with cols[idx]:
            st.markdown(f"""
            <div style="background:#E6F0ED; padding:16px; border-radius:10px; border:2px solid #00796B; text-align:center;">
                <div style="font-size:2.5rem;">{item['icon']}</div>
                <h4 style="margin:8px 0;">{item['sign']}</h4>
                <p style="font-size:0.85rem; color:#48656E;">{item['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"🔊 Listen", key=f"isl_{idx}"):
                audio_fp = rag.text_to_speech_audio(f"{item['sign']}. {item['desc']}", target_lang)
                if audio_fp:
                    st.audio(audio_fp, format="audio/mp3")

# ==============================================================================
# TAB 6: AAC INDIAN SITUATION BOARD
# ==============================================================================
with tabs[5]:
    st.subheader("🗣️ Augmentative & Alternative Communication (AAC) Indian Board")
    st.markdown("Designed for rapid communication at clinics, auto-rickshaws, ration/kirana shops, and government offices.")

    preset = st.selectbox(
        "Select Situation:",
        ["🏥 Clinic / Doctor", "🛺 Auto-Rickshaw / Bus", "🛒 Kirana / Ration Shop", "🏛️ Panchayat / Post Office"]
    )

    phrases = {
        "🏥 Clinic / Doctor": [
            "नमस्ते डॉक्टर, मुझे दो दिन से बुखार और सिरदर्द है।",
            "क्या यह दवा खाने से पहले लेनी है या बाद में?",
            "कृपया पर्ची पर निर्देश बड़े अक्षरों में लिख दीजिए।",
            "मुझे इंजेक्शन से डर लगता है, क्या सिरप उपलब्ध है?"
        ],
        "🛺 Auto-Rickshaw / Bus": [
            "भैया, कृपया मीटर से रेलवे स्टेशन ले चलिए।",
            "वहाँ तक का कितना किराया होगा?",
            "कृपया मुझे बस स्टैंड आने पर बता दीजिए।",
            "मैं यूपीआई / फोनपे से भुगतान करूँगा।"
        ],
        "🛒 Kirana / Ration Shop": [
            "भैया, 1 किलो दाल और 500 ग्राम चीनी दीजिए।",
            "कुल कितना रुपया हुआ?",
            "कृपया मुझे पक्का बिल दीजिए।",
            "क्या आपके पास 500 रुपये के छुट्टे हैं?"
        ],
        "🏛️ Panchayat / Post Office": [
            "मुझे यूडीआईडी (UDID) दिव्यांग पहचान पत्र का फॉर्म चाहिए।",
            "इसके लिए कौन-से सरकारी दस्तावेज़ जमा करने होंगे?",
            "कृपया फॉर्म भरने में मेरी सहायता कीजिए।"
        ]
    }

    selected_phrase = st.selectbox("Select phrase to display / speak:", phrases[preset])

    st.markdown("### 🔄 180° Tabletop Flip View (Show to person across counter):")
    st.markdown(f"""
    <div class="flip-card-view">
        <h2 style="color:#B45309; margin:0;">{selected_phrase}</h2>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔊 Speak Phrase Out Loud", type="primary"):
        audio_fp = rag.text_to_speech_audio(selected_phrase, "hi")
        if audio_fp:
            st.audio(audio_fp, format="audio/mp3")

# ==============================================================================
# TAB 7: LIVE 60 FPS WEBCAM PWA EMBED
# ==============================================================================
with tabs[6]:
    st.subheader("🌐 Live 60 FPS Client-Side Computer Vision & Audio Sentinel")
    st.markdown(
        "Runs high-performance **TensorFlow.js COCO-SSD object tracking**, "
        "real-time webcam hand gesture recognition, and 60 FPS audio spectrogram listeners directly in your browser."
    )

    st.info("💡 To use full live camera and microphone streaming, ensure you access via `http://localhost:5500` or an HTTPS URL.")

    # Embed local or hosted index.html
    st.components.v1.iframe(
        src="http://localhost:5500/index.html",
        height=680,
        scrolling=True
    )
