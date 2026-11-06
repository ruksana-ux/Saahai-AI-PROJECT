# Sahaaya AI (सहाय) — 100% Pure Python Assistive Platform for India

An inclusive, multimodal, multilingual assistive technology platform written **100% in Python**, designed specifically for the socioeconomic, linguistic, and infrastructural realities of India.

Empowers **visually impaired, deaf, hard-of-hearing, nonspeaking, and deafblind** children and adults to learn, communicate, navigate streets safely, access essential public services, and achieve daily independence.

---

## 🇮🇳 Real-World Context & Technology Gaps in India

According to official demographic assessments (Census of India, LASI, and NSS):
- Approximately **2.21% of India's population (~26.8 million citizens)** lives with a disability.
- **70% to 71%** of persons with disabilities in India lack access to necessary assistive hardware and software (WHO-UNICEF GReAT report).
- **67.4%** of all assistive technology items in India are paid for **completely out-of-pocket** by low-income families.
- Over **15.5%** of India's disability burden is concentrated in **Uttar Pradesh**, followed by **Maharashtra (11.05%)** and **Bihar (8.69%)**, where advanced medical aids are largely unaffordable.

### How Sahaaya AI Fixes Existing Failures in India:
| Existing Solution in India | Documented Shortcomings | Sahaaya AI (100% Python) Solution |
| :--- | :--- | :--- |
| **RBI MANI App** | **No counterfeit detection**, **zero support for coins**, fails on crumpled/older notes in dim light, voice search fails ("MANI" vs "Money"). | Identifies **banknotes (₹10–₹500)** AND **coins (₹5, ₹10, and 12-sided ₹20 dodecagon)**; provides **anti-counterfeit verification checklists** (tactile bleed lines, watermark, color-shifting thread); audio readouts. |
| **Google Lookout / Seeing AI** | English-first, struggles with cluttered Indian streets, makes unverified AI claims. | **Localized across 9 Indian languages** with ground-plane edge analysis for Indian hazards (open storm drains/nalas, potholes, hanging wires). |
| **Traditional White Canes / SmartCane** | High cost (₹3,000–₹15,000+), cannot detect low-hanging overhead wires or open storm drains. | Multi-modal **Street Hazard Vision** providing directional audio beacons, tactile vibration tiers, and emergency GPS SOS broadcast. |
| **Western AAC Apps** | Prohibitive subscription fees ($100–$300), culturally alien icons, lack of Indian languages. | Pre-configured Indian everyday situations (**Clinic, Auto-rickshaw, Kirana/Ration shop, Panchayat**) with 180° tabletop flip card views. |
| **Standalone ISL Dictionaries** | Video lists disconnected from school textbooks and classroom assessments. | **Accessible Classroom & ISL Studio** connecting worksheets, audio read-alouds, comprehension quizzes, and topic-linked sign vocabulary. |

---

## 🏗️ 100% Pure Python Architecture

```
saahai-ai-project/
│
├── app.py                   # Streamlit Main Application (7 Interactive Modules)
├── rag_engine.py            # Hybrid TF-IDF Vector Search & LLM Generation (Gemini / OpenAI / Offline)
├── cv_engine.py             # Computer Vision: Street hazards, potholes, open nalas, low wires
├── currency_engine.py       # Banknote & Coin CV Classifier + Anti-Counterfeit Checklist
├── classroom_engine.py      # NCERT Worksheet Reader, Summarizer & Comprehension Quiz
├── isl_engine.py            # Indian Sign Language (ISL) Education & Quiz Engine
├── aac_engine.py            # Multilingual AAC Engine with 180° Tabletop Flip Cards
│
├── knowledge_base/          # Verified Indian Datasets
│   ├── demographics_data.json   # Census, LASI, State Burden (UP, Bihar, Maharashtra)
│   ├── welfare_schemes.json     # ADIP eligibility (<₹15k/mo), UDID, RPwD Act 2016
│   └── tech_gap_analysis.json   # RBI MANI, Kibo, SmartCane gap comparisons
│
├── .streamlit/config.toml   # Accessible High-Contrast Theme
├── requirements.txt         # Pure Python Dependencies (Streamlit, gTTS, Pillow, OpenCV, NumPy)
└── .gitignore               # Git Rules
```

---

## 🚀 Live Cloud Deployment via GitHub & Streamlit Community Cloud

### Step 1: Push Changes to GitHub
```powershell
git add .
git commit -m "refactor: convert entire platform to 100% pure Python architecture"
git push origin main
```

### Step 2: Deploy to Streamlit Community Cloud (Free 24/7)
1. Go to [share.streamlit.io](https://share.streamlit.io/) and click **Continue with GitHub**.
2. Click **Create app** (or **New app**).
3. Select:
   - **Repository**: `ruksana-ux/Saahai-AI-PROJECT`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. *(Optional)* Add your Gemini API key in **Advanced settings** -> **Secrets**:
   ```toml
   GEMINI_API_KEY = "your-google-gemini-key"
   ```
   *(Note: The app works out of the box even without any API key using its built-in offline neural semantic RAG engine).*
5. Click **Deploy!** 🚀

---

## 🛠️ Local Development & Testing

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run Streamlit application
streamlit run app.py
```
