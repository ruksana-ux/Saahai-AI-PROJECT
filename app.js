/**
 * Sahaaya AI — Accessibility Without Barriers (सहाय)
 * Inclusive, Multilingual, Multimodal Assistive Engine for India
 */

(function () {
  'use strict';

  // --- 1. SUPPORTED INDIAN LANGUAGES ---
  const LANGS = [
    { code: "en-IN", name: "English (India)", native: "English" },
    { code: "hi-IN", name: "Hindi", native: "हिन्दी" },
    { code: "ta-IN", name: "Tamil", native: "தமிழ்" },
    { code: "kn-IN", name: "Kannada", native: "ಕನ್ನಡ" },
    { code: "bn-IN", name: "Bengali", native: "বাংলা" },
    { code: "te-IN", name: "Telugu", native: "తెలుగు" },
    { code: "ml-IN", name: "Malayalam", native: "മലയാളം" },
    { code: "mr-IN", name: "Marathi", native: "मराठी" },
    { code: "gu-IN", name: "Gujarati", native: "ગુજરાતી" }
  ];

  // Helper DOM lookup
  const $ = (id) => document.getElementById(id);

  // App State
  let currentLang = "hi-IN";
  let voiceGuideEnabled = false;
  let synthVoices = [];
  let currentProfile = "all";
  let sentence = [];

  // Initialize Speech Synthesis
  function loadVoices() {
    try {
      if (window.speechSynthesis) {
        synthVoices = window.speechSynthesis.getVoices();
      }
    } catch (e) {
      console.warn("Speech synthesis voices error:", e);
    }
  }

  if (typeof window !== "undefined" && window.speechSynthesis) {
    window.speechSynthesis.onvoiceschanged = loadVoices;
    loadVoices();
  }

  function stopSpeech() {
    try {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    } catch (e) { }
  }

  function speakText(text, rate = 0.9, onEndCallback = null) {
    if (!window.speechSynthesis || !text || !text.trim()) return;
    stopSpeech();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = currentLang;
    utterance.rate = rate;

    // Find best matching voice for selected language
    const langPrefix = currentLang.slice(0, 2).toLowerCase();
    const exactVoice = synthVoices.find(v => v.lang.replace('_', '-').toLowerCase() === currentLang.toLowerCase());
    const prefixVoice = synthVoices.find(v => v.lang.slice(0, 2).toLowerCase() === langPrefix);

    if (exactVoice) {
      utterance.voice = exactVoice;
    } else if (prefixVoice) {
      utterance.voice = prefixVoice;
    }

    if (onEndCallback) {
      utterance.onend = onEndCallback;
    }

    window.speechSynthesis.speak(utterance);
  }

  // Haptic Tactile Vibration Engine
  function hapticBuzz(pattern) {
    try {
      if (navigator.vibrate) {
        navigator.vibrate(pattern);
      }
    } catch (e) { }
  }

  // Audio Synthesizer Beep for emergency & alerts without audio files
  function playAudioTone(freq = 880, duration = 300, type = 'sine') {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, ctx.currentTime);
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + duration / 1000);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration / 1000);
    } catch (e) { }
  }

  // Screen Reader Voice Guide
  function guideVoice(message) {
    if (voiceGuideEnabled) {
      speakText(message, 1.0);
    }
  }

  // --- 2. POPULATE TOOLBAR CONTROLS ---
  function initToolbar() {
    const langSelect = $("lang-select");
    LANGS.forEach(lang => {
      const opt = document.createElement("option");
      opt.value = lang.code;
      opt.textContent = `${lang.native} (${lang.name})`;
      if (lang.code === currentLang) opt.selected = true;
      langSelect.appendChild(opt);
    });

    langSelect.addEventListener("change", (e) => {
      currentLang = e.target.value;
      const selected = LANGS.find(l => l.code === currentLang);
      guideVoice(`Language changed to ${selected.name}`);
      updateAllLanguageViews();
    });

    // Theme selector
    const themeSelect = $("theme-select");
    const savedTheme = localStorage.getItem("sahaaya-theme") || "light";
    document.documentElement.setAttribute("data-theme", savedTheme);
    themeSelect.value = savedTheme;

    themeSelect.addEventListener("change", (e) => {
      const theme = e.target.value;
      document.documentElement.setAttribute("data-theme", theme);
      localStorage.setItem("sahaaya-theme", theme);
      guideVoice(`Theme set to ${theme}`);
    });

    // Font size selector
    const fontSelect = $("font-size-select");
    const savedFont = localStorage.getItem("sahaaya-font") || "normal";
    document.documentElement.setAttribute("data-font-size", savedFont);
    fontSelect.value = savedFont;

    fontSelect.addEventListener("change", (e) => {
      const size = e.target.value;
      document.documentElement.setAttribute("data-font-size", size);
      localStorage.setItem("sahaaya-font", size);
      guideVoice(`Font size set to ${size}`);
    });

    // Toggle voice guidance
    const voiceGuideBtn = $("toggle-screen-voice");
    voiceGuideBtn.addEventListener("click", () => {
      voiceGuideEnabled = !voiceGuideEnabled;
      voiceGuideBtn.setAttribute("aria-pressed", voiceGuideEnabled);
      voiceGuideBtn.textContent = voiceGuideEnabled ? "🔊 Spoken Guide: ON" : "🔇 Spoken Guide: OFF";
      voiceGuideBtn.className = voiceGuideEnabled ? "btn-accent" : "btn-primary";
      if (voiceGuideEnabled) {
        speakText("Spoken guidance activated. Navigation and buttons will be announced.");
      }
    });
  }

  // --- 3. ADAPTIVE PROFILE SWITCHER ---
  function initProfiles() {
    const profileButtons = [
      { id: "prof-all", role: "all", desc: "All tools mode enabled" },
      { id: "prof-blind", role: "blind", desc: "Visually impaired profile: high contrast, audio readouts, rupee scanner, and street hazard sensor prioritised." },
      { id: "prof-deaf", role: "deaf", desc: "Deaf profile: 2-way communicator, visual alerts, and sign language studio enabled." },
      { id: "prof-speech", role: "speech", desc: "Nonspeaking profile: AAC communication boards and rapid speech composer enabled." },
      { id: "prof-deafblind", role: "deafblind", desc: "Deafblind profile: Tactile haptic vibration engine and morse signals activated." }
    ];

    profileButtons.forEach(p => {
      const btn = $(p.id);
      if (!btn) return;
      btn.addEventListener("click", () => {
        profileButtons.forEach(o => {
          const el = $(o.id);
          el.classList.remove("active");
          el.setAttribute("aria-checked", "false");
        });
        btn.classList.add("active");
        btn.setAttribute("aria-checked", "true");
        currentProfile = p.role;
        applyProfile(p.role);
        guideVoice(p.desc);
        hapticBuzz(60);
      });
    });
  }

  function applyProfile(role) {
    if (role === "blind") {
      document.documentElement.setAttribute("data-theme", "high-contrast-yellow");
      $("theme-select").value = "high-contrast-yellow";
      switchTab("tab-classroom");
    } else if (role === "deaf") {
      switchTab("tab-comm");
    } else if (role === "speech") {
      switchTab("tab-aac");
    } else if (role === "deafblind") {
      document.documentElement.setAttribute("data-theme", "high-contrast-white");
      $("theme-select").value = "high-contrast-white";
      switchTab("tab-alerts");
      hapticBuzz([200, 100, 200]);
    }
  }

  // --- 4. TAB NAVIGATION ---
  const TABS = [
    { btnId: "tab-classroom", panelId: "panel-classroom", title: "Classroom Assistant" },
    { btnId: "tab-comm", panelId: "panel-comm", title: "Two-Way Multilingual Communicator" },
    { btnId: "tab-aac", panelId: "panel-aac", title: "Augmentative Communication AAC" },
    { btnId: "tab-journey", panelId: "panel-journey", title: "Safer Journey Street Mobility" },
    { btnId: "tab-isl", panelId: "panel-isl", title: "Indian Sign Language Studio" },
    { btnId: "tab-alerts", panelId: "panel-alerts", title: "Multisensory Alerts and Haptics" },
    { btnId: "tab-currency", panelId: "panel-currency", title: "Indian Rupee and Medicine Identifier" },
    { btnId: "tab-schemes", panelId: "panel-schemes", title: "India Demographics and Schemes" }
  ];

  function switchTab(btnId) {
    TABS.forEach(t => {
      const btn = $(t.btnId);
      const panel = $(t.panelId);
      const isSelected = (t.btnId === btnId);
      if (btn) btn.setAttribute("aria-selected", isSelected);
      if (panel) panel.hidden = !isSelected;
      if (isSelected) {
        guideVoice(`Viewing ${t.title}`);
      }
    });
    stopSpeech();
  }

  function initTabs() {
    TABS.forEach(t => {
      const btn = $(t.btnId);
      if (btn) {
        btn.addEventListener("click", () => {
          hapticBuzz(35);
          switchTab(t.btnId);
        });
      }
    });
  }

  // --- 5. MODULE 1: ACCESSIBLE CLASSROOM ASSISTANT ---
  const CLASSROOM_LESSONS = {
    evs: {
      text: "How Plants Make Food (प्रकाश संश्लेषण): Green plants use sunlight, water from the soil, and carbon dioxide from the air to prepare their own food. This process is called Photosynthesis. During this process, plants release oxygen into the atmosphere, which all humans and animals breathe. Chlorophyll in leaves gives them their green color.",
      quiz: [
        { q: "What gas do green plants release during photosynthesis?", options: ["Oxygen", "Carbon dioxide", "Nitrogen"], ans: 0 },
        { q: "What gives green leaves their color?", options: ["Sunlight", "Chlorophyll", "Water"], ans: 1 },
        { q: "Where do plants absorb water from?", options: ["Soil / Roots", "Clouds", "Air"], ans: 0 }
      ],
      signs: ["Plant", "Sun", "Water", "Food", "Air"]
    },
    civics: {
      text: "The Rights of Persons with Disabilities (RPwD) Act 2016 guarantees equal opportunity, non-discrimination, and full participation in society. It mandates accessibility in schools, colleges, and public buildings, providing 4% reservation in government jobs and 5% in higher education for persons with benchmark disabilities.",
      quiz: [
        { q: "Which act guarantees equal opportunity in India?", options: ["RPwD Act 2016", "Motor Vehicle Act", "Companies Act"], ans: 0 },
        { q: "What percent reservation in government jobs is mandated?", options: ["2%", "4%", "10%"], ans: 1 },
        { q: "What does the act mandate for public buildings?", options: ["Accessible ramps & lifts", "Only stairs", "No change"], ans: 0 }
      ],
      signs: ["School", "Law / Rights", "Help", "Equal", "Study"]
    },
    math: {
      text: "Everyday Kirana Bill: Rahul bought 1 kg rice for ₹50, 1 packet milk for ₹28, and soap for ₹22. Total amount = 50 + 28 + 22 = ₹100. Rahul gave a ₹200 note to the shopkeeper. Change to receive = 200 - 100 = ₹100.",
      quiz: [
        { q: "What was the total cost of the items?", options: ["₹100", "₹80", "₹120"], ans: 0 },
        { q: "Which note did Rahul hand to the shopkeeper?", options: ["₹500 note", "₹200 note", "₹50 note"], ans: 1 },
        { q: "How much change should the shopkeeper return?", options: ["₹100", "₹50", "₹20"], ans: 0 }
      ],
      signs: ["Money / Rupee", "Buy", "Number", "Yes", "Thank You"]
    },
    notice: {
      text: "School Circular: Inclusive Annual Sports Day will take place on 14th November. Accessible sports including Goalball for visually impaired students and Sign-language guided athletics are scheduled. Mid-day meal will feature special nutritious khichdi and fresh fruit.",
      quiz: [
        { q: "When is the Inclusive Sports Day?", options: ["14th November", "26th January", "15th August"], ans: 0 },
        { q: "Which accessible sport is listed for visually impaired students?", options: ["Goalball", "Tennis", "Archery"], ans: 0 },
        { q: "What special item is included in the mid-day meal?", options: ["Nutritious khichdi & fruit", "Pizza", "Biscuits only"], ans: 0 }
      ],
      signs: ["School", "Play / Sports", "Food", "Friend", "Day"]
    }
  };

  let activeQuizData = [];
  let currentQuizStep = 0;
  let quizScore = 0;

  function initClassroomModule() {
    const sampleSelect = $("sample-sheet-select");
    const textArea = $("classroom-text");
    const rateInput = $("classroom-rate");
    const rateDisplay = $("rate-display");
    const quizArea = $("classroom-quiz-area");

    function loadSelectedLesson() {
      const lessonKey = sampleSelect.value;
      const lesson = CLASSROOM_LESSONS[lessonKey];
      if (lesson) {
        textArea.value = lesson.text;
        activeQuizData = lesson.quiz;
        renderLessonSigns(lesson.signs);
        quizArea.hidden = true;
      }
    }

    sampleSelect.addEventListener("change", loadSelectedLesson);
    loadSelectedLesson();

    rateInput.addEventListener("input", () => {
      rateDisplay.textContent = `${rateInput.value}x`;
    });

    $("btn-read-classroom").addEventListener("click", () => {
      const speed = parseFloat(rateInput.value) || 0.9;
      hapticBuzz(40);
      speakText(textArea.value, speed);
    });

    $("btn-stop-classroom").addEventListener("click", () => {
      stopSpeech();
    });

    $("btn-font-zoom").addEventListener("click", () => {
      const currentSize = parseInt(window.getComputedStyle(textArea).fontSize, 10);
      const newSize = currentSize >= 28 ? 18 : currentSize + 4;
      textArea.style.fontSize = `${newSize}px`;
      hapticBuzz(30);
      guideVoice(`Font size is now ${newSize} pixels`);
    });

    $("btn-quiz-classroom").addEventListener("click", () => {
      quizArea.hidden = false;
      currentQuizStep = 0;
      quizScore = 0;
      renderQuizQuestion();
      quizArea.scrollIntoView({ behavior: "smooth" });
    });
  }

  function renderLessonSigns(signList) {
    const container = $("classroom-isl-pills");
    container.innerHTML = "";
    signList.forEach(sign => {
      const pill = document.createElement("button");
      pill.className = "cat-btn";
      pill.textContent = `🤟 ${sign}`;
      pill.onclick = () => {
        switchTab("tab-isl");
        filterISLBySearch(sign);
      };
      container.appendChild(pill);
    });
  }

  function renderQuizQuestion() {
    const quizContent = $("quiz-content");
    const feedback = $("quiz-feedback");
    feedback.textContent = "";

    if (currentQuizStep >= activeQuizData.length) {
      quizContent.innerHTML = `
        <div style="text-align: center; padding: 14px;">
          <h4>🎉 Quiz Complete!</h4>
          <p style="font-size: 1.2rem; font-weight: 800; color: var(--success); margin: 8px 0;">Your Score: ${quizScore} / ${activeQuizData.length}</p>
          <button class="btn-primary" onclick="document.getElementById('btn-quiz-classroom').click()">Retry Quiz</button>
        </div>
      `;
      speakText(`Quiz complete. You scored ${quizScore} out of ${activeQuizData.length}. Great job!`);
      return;
    }

    const currentQ = activeQuizData[currentQuizStep];
    let html = `
      <div class="quiz-question">Question ${currentQuizStep + 1} of ${activeQuizData.length}: ${currentQ.q}</div>
      <div class="quiz-options">
    `;

    currentQ.options.forEach((opt, idx) => {
      html += `<button class="quiz-opt-btn" data-opt-idx="${idx}">${String.fromCharCode(65 + idx)}. ${opt}</button>`;
    });

    html += `</div>`;
    quizContent.innerHTML = html;

    speakText(`Question ${currentQuizStep + 1}: ${currentQ.q}`);

    quizContent.querySelectorAll(".quiz-opt-btn").forEach(btn => {
      btn.addEventListener("click", (e) => {
        const picked = parseInt(btn.dataset.optIdx, 10);
        if (picked === currentQ.ans) {
          btn.classList.add("correct");
          feedback.textContent = "✅ Correct Answer! Excellent.";
          feedback.style.color = "var(--success)";
          quizScore++;
          hapticBuzz([100, 50, 100]);
          speakText("Correct answer!", 1.0, () => {
            setTimeout(() => {
              currentQuizStep++;
              renderQuizQuestion();
            }, 700);
          });
        } else {
          btn.classList.add("incorrect");
          feedback.textContent = `❌ Incorrect. The correct answer was: ${currentQ.options[currentQ.ans]}`;
          feedback.style.color = "var(--danger)";
          hapticBuzz([250, 80, 250]);
          speakText(`Incorrect. The correct answer was ${currentQ.options[currentQ.ans]}`, 1.0, () => {
            setTimeout(() => {
              currentQuizStep++;
              renderQuizQuestion();
            }, 1200);
          });
        }
      });
    });
  }

  // --- 6. MODULE 2: TWO-WAY MULTILINGUAL COMMUNICATOR ---
  const SITUATION_PHRASES = {
    clinic: [
      { text: "नमस्ते डॉक्टर, मुझे दो दिन से तेज बुखार और सिरदर्द है।", eng: "Hello Doctor, I have had high fever and headache for 2 days." },
      { text: "क्या यह दवा खाने से पहले लेनी है या बाद में?", eng: "Should this medicine be taken before or after meals?" },
      { text: "कृपया पर्ची पर निर्देश बड़े अक्षरों में लिख दीजिए।", eng: "Please write the instructions on the prescription in big letters." },
      { text: "मुझे इंजेक्शन से बहुत डर लगता है, क्या सिरप उपलब्ध है?", eng: "I am scared of injections, is a syrup available?" }
    ],
    auto: [
      { text: "भैया, कृपया मीटर से रेलवे स्टेशन ले चलिए।", eng: "Brother, please take me to the Railway Station by meter." },
      { text: "वहाँ तक का कितना किराया होगा?", eng: "How much will the fare be till there?" },
      { text: "कृपया मुझे बस स्टैंड आने पर बता दीजिए।", eng: "Please let me know when the Bus Stand arrives." },
      { text: "मैं यूपीआई / क्यूआर कोड से भुगतान करूँगा।", eng: "I will pay using UPI / QR code." }
    ],
    kirana: [
      { text: "भैया, 1 किलो अरहर दाल और आधा किलो चीनी दीजिए।", eng: "Brother, please give 1 kg Arhar Dal and 500g sugar." },
      { text: "कुल कितना रुपया हुआ?", eng: "What is the total amount in Rupees?" },
      { text: "कृपया मुझे पक्का बिल दीजिए।", eng: "Please give me a printed receipt." },
      { text: "क्या आपके पास 500 रुपये के छुट्टे हैं?", eng: "Do you have change for a 500 Rupee note?" }
    ],
    school: [
      { text: "नमस्ते मैडम, मुझे आज का गृहकार्य समझने में कठिनाई हुई।", eng: "Hello Madam, I had difficulty understanding today's homework." },
      { text: "क्या मुझे परीक्षा के लिए अतिरिक्त 20 मिनट मिलेंगे?", eng: "Will I get 20 minutes extra time for the exam?" },
      { text: "कृपया यह प्रश्न मुझे सांकेतिक भाषा (ISL) में समझाइए।", eng: "Please explain this question to me in Indian Sign Language." }
    ],
    govt: [
      { text: "मुझे यूडीआईडी (UDID) दिव्यांग पहचान पत्र का नवीनीकरण कराना है।", eng: "I need to renew my UDID Disability Identity Card." },
      { text: "इसके लिए कौन-से सरकारी दस्तावेज़ जमा करने होंगे?", eng: "Which official documents do I need to submit?" },
      { text: "कृपया फॉर्म भरने में मेरी सहायता कीजिए।", eng: "Please assist me with filling out this form." }
    ]
  };

  const QUICK_REPLIES = [
    { hi: "हाँ", en: "Yes", ta: "ஆம்", kn: "ಹೌದು", te: "అవును", bn: "হ্যাঁ", ml: "അതെ" },
    { hi: "नहीं", en: "No", ta: "இல்லை", kn: "ಇಲ್ಲ", te: "కాదు", bn: "না", ml: "ഇല്ല" },
    { hi: "कृपया लिख कर बताइए", en: "Please write it down", ta: "தயவுசெய்து எழுதி காட்டுங்கள்", kn: "ದಯವಿಟ್ಟು ಬರೆದು ತೋರಿಸಿ", te: "దయచేసి రాసి చూపించండి", bn: "দয়া করে লিখে দেখান", ml: "ദയവായി എഴുതി കാണിക്കൂ" },
    { hi: "कितने रुपये हुए?", en: "How many Rupees?", ta: "எத்தனை ரூபாய்?", kn: "ಎಷ್ಟು ರೂಪಾಯಿ?", te: "ఎంత రూపాయలు?", bn: "কত টাকা হয়েছে?", ml: "എത്ര രൂപയായി?" },
    { hi: "एक मिनट रुकिए", en: "Wait one moment", ta: "ஒரு நிமிடம் காத்திருங்கள்", kn: "ಒಂದು ನಿಮಿಷ ಕಾಯಿರಿ", te: "ఒక్క నిమిషం ఆగండి", bn: "এক মিনিট অপেক্ষা করুন", ml: "ഒരു മിനിറ്റ് കാക്കൂ" },
    { hi: "धन्यवाद", en: "Thank you", ta: "நன்றி", kn: "ಧನ್ಯವಾದಗಳು", te: "ధన్యవాదాలు", bn: "ধন্যবাদ", ml: "നന്ദി" }
  ];

  let speechRecognition = null;
  let isListening = false;

  function initCommModule() {
    const scenarioSelect = $("comm-scenario-select");
    const partnerCard = $("partner-card");
    const partnerMsg = $("partner-msg");
    const partnerSub = $("partner-sub");
    const flipBtn = $("btn-flip-card");
    const speakPartnerBtn = $("btn-speak-partner-msg");
    const quickChips = $("comm-quick-chips");

    function updateScenario() {
      const scenario = scenarioSelect.value;
      const phrases = SITUATION_PHRASES[scenario] || SITUATION_PHRASES.clinic;
      partnerMsg.textContent = `"${phrases[0].text}"`;
      partnerSub.textContent = `("${phrases[0].eng}")`;

      // Render situation phrase buttons
      quickChips.innerHTML = "";
      phrases.forEach(p => {
        const btn = document.createElement("button");
        btn.className = "cat-btn";
        btn.textContent = p.eng.slice(0, 24) + "...";
        btn.title = p.text;
        btn.onclick = () => {
          partnerMsg.textContent = `"${p.text}"`;
          partnerSub.textContent = `("${p.eng}")`;
          hapticBuzz(35);
          speakText(p.text);
        };
        quickChips.appendChild(btn);
      });

      // Append universal quick replies
      QUICK_REPLIES.forEach(qr => {
        const btn = document.createElement("button");
        btn.className = "cat-btn";
        btn.textContent = `⚡ ${qr.en} / ${qr.hi}`;
        btn.onclick = () => {
          const phrase = getTranslatedText(qr);
          partnerMsg.textContent = `"${phrase}"`;
          partnerSub.textContent = `("${qr.en}")`;
          hapticBuzz(30);
          speakText(phrase);
        };
        quickChips.appendChild(btn);
      });
    }

    scenarioSelect.addEventListener("change", updateScenario);
    updateScenario();

    flipBtn.addEventListener("click", () => {
      partnerCard.classList.toggle("flipped");
      const isFlipped = partnerCard.classList.contains("flipped");
      flipBtn.textContent = isFlipped ? "🔄 Normal View" : "🔄 Flip Screen (180°)";
      hapticBuzz(40);
      guideVoice(isFlipped ? "Screen flipped for partner" : "Screen in normal orientation");
    });

    speakPartnerBtn.addEventListener("click", () => {
      const cleanText = partnerMsg.textContent.replace(/["']/g, "");
      speakText(cleanText);
    });

    // Live Captions for Hearing Impaired
    const startCaptionsBtn = $("btn-start-captions");
    const clearCaptionsBtn = $("btn-clear-captions");
    const captionsBox = $("comm-captions-box");
    const statusNote = $("comm-sr-status");

    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRec) {
      statusNote.textContent = "⚠️ Browser Speech Recognition is unavailable. Use Chrome on Android or Desktop.";
      startCaptionsBtn.disabled = true;
    } else {
      speechRecognition = new SpeechRec();
      speechRecognition.continuous = true;
      speechRecognition.interimResults = true;

      speechRecognition.onresult = (event) => {
        let finalStr = "";
        let interimStr = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalStr += event.results[i][0].transcript + " ";
          } else {
            interimStr += event.results[i][0].transcript;
          }
        }
        if (finalStr) {
          captionsBox.appendChild(document.createTextNode(finalStr + "\n"));
        }
        const existingInterim = captionsBox.querySelector(".interim-text");
        if (existingInterim) existingInterim.remove();
        if (interimStr) {
          const iEl = document.createElement("i");
          iEl.className = "interim-text";
          iEl.textContent = interimStr;
          captionsBox.appendChild(iEl);
        }
        captionsBox.scrollTop = captionsBox.scrollHeight;
      };

      speechRecognition.onerror = (e) => {
        statusNote.textContent = `Speech error: ${e.error}. Check microphone permissions.`;
        isListening = false;
        startCaptionsBtn.textContent = "🎙️ Start Listening";
      };

      speechRecognition.onend = () => {
        if (isListening) {
          try { speechRecognition.start(); } catch (err) { }
        }
      };

      startCaptionsBtn.addEventListener("click", () => {
        if (isListening) {
          isListening = false;
          speechRecognition.stop();
          startCaptionsBtn.textContent = "🎙️ Start Listening";
          statusNote.textContent = "Captions paused.";
          hapticBuzz(40);
        } else {
          speechRecognition.lang = currentLang;
          try {
            speechRecognition.start();
            isListening = true;
            startCaptionsBtn.textContent = "⏹️ Stop Captions";
            statusNote.textContent = `Listening in ${currentLang}... Speak clearly near phone microphone.`;
            hapticBuzz([60, 40, 60]);
          } catch (err) {
            statusNote.textContent = "Could not activate microphone.";
          }
        }
      });

      clearCaptionsBtn.addEventListener("click", () => {
        captionsBox.innerHTML = "";
        hapticBuzz(25);
      });
    }
  }

  function getTranslatedText(obj) {
    const langKey = currentLang.slice(0, 2);
    return obj[langKey] || obj.hi || obj.en;
  }

  // --- 7. MODULE 3: AUGMENTATIVE COMMUNICATION (AAC) ---
  const AAC_DATA = [
    // Emergency & Help
    { id: "e1", cat: "emergency", icon: "🆘", en: "Please help me", hi: "कृपया मेरी मदद करें", ta: "தயவுசெய்து எனக்கு உதவுங்கள்", kn: "ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಿ", bn: "দয়া করে আমাকে সাহায্য করুন", te: "దయచేసి నాకు సహాయం చేయండి", ml: "ദയവായി എന്നെ സഹായിക്കൂ" },
    { id: "e2", cat: "emergency", icon: "🤕", en: "I am in severe pain", hi: "मुझे बहुत तेज दर्द हो रहा है", ta: "எனக்கு கடுமையான வலி உள்ளது", kn: "ನನಗೆ ತೀವ್ರ ನೋವಾಗುತ್ತಿದೆ", bn: "আমার খুব তীব্র ব্যথা করছে", te: "నాకు విపరీతమైన నొప్పి ఉంది", ml: "എനിക്ക് കഠിനമായ വേദനയുണ്ട്" },
    { id: "e3", cat: "emergency", icon: "🏥", en: "Take me to hospital", hi: "मुझे अस्पताल ले चलिए", ta: "என்னை மருத்துவமனைக்கு அழைத்துச் செல்லுங்கள்", kn: "ನನ್ನನ್ನು ಆಸ್ಪತ್ರೆಗೆ ಕರೆದೊಯ್ಯಿರಿ", bn: "আমাকে হাসপাতালে নিয়ে চলুন", te: "నన్ను ఆసుపత్రికి తీసుకెళ్లండి", ml: "എന്നെ ആശുപത്രിയിൽ എത്തിക്കൂ" },
    { id: "e4", cat: "emergency", icon: "📞", en: "Call my family", hi: "मेरे परिवार को फोन मिलाइए", ta: "என் குடும்பத்திற்கு போன் செய்யுங்கள்", kn: "ನನ್ನ ಕುಟುಂಬಕ್ಕೆ ಕರೆ ಮಾಡಿ", bn: "আমার পরিবারকে ফোন করুন", te: "నా కుటుంబానికి ఫోన్ చేయండి", ml: "എന്റെ വീട്ടിലേക്ക് വിളിക്കൂ" },

    // Health & Medicine
    { id: "h1", cat: "health", icon: "💊", en: "I need my medicine", hi: "मुझे मेरी दवा चाहिए", ta: "எனக்கு மருந்து வேண்டும்", kn: "ನನಗೆ ಔಷಧ ಬೇಕು", bn: "আমার ওষুধ চাই", te: "నాకు మందు కావాలి", ml: "എനിക്ക് മരുന്ന് വേണം" },
    { id: "h2", cat: "health", icon: "🩺", en: "Call the doctor", hi: "डॉक्टर को बुलाइए", ta: "மருத்துவரை அழையுங்கள்", kn: "ವೈದ್ಯರನ್ನು ಕರೆಯಿರಿ", bn: "ডাক্তার ডাকুন", te: "డాక్టర్ ను పిలవండి", ml: "ഡോക്ടറെ വിളിക്കൂ" },
    { id: "h3", cat: "health", icon: "🌀", en: "I feel dizzy and weak", hi: "मुझे चक्कर आ रहे हैं और कमजोरी है", ta: "எனக்கு தலைச்சுற்றலாக உள்ளது", kn: "ನನಗೆ ತಲೆತಿರುಗುತ್ತಿದೆ", bn: "আমার মাথা ঘুরছে ও দুর্বল লাগছে", te: "నాకు కళ్ళు తిరుగుతున్నాయి", ml: "എനിക്ക് തലകറങ്ങുന്നു" },
    { id: "h4", cat: "health", icon: "✍️", en: "Please write it on paper", hi: "कृपया कागज़ पर लिख दीजिए", ta: "காகிதத்தில் எழுதி காட்டுங்கள்", kn: "ದಯವಿಟ್ಟು ಕಾಗದದಲ್ಲಿ ಬರೆಯಿರಿ", bn: "দয়া করে কাগজে লিখে দিন", te: "దయచేసి కాగితంపై రాయండి", ml: "ദയവായി കടലാസിൽ എഴുതി തരൂ" },

    // Travel & Transport
    { id: "t1", cat: "travel", icon: "🛺", en: "Auto-rickshaw stand", hi: "ऑटो रिक्शा स्टैंड कहाँ है?", ta: "ஆட்டோ ஸ்டாண்ட் எங்கே?", kn: "ಆಟೋ ನಿಲ್ದಾಣ ಎಲ್ಲಿದೆ?", bn: "অটো স্ট্যান্ড কোথায়?", te: "ఆటో స్టాండ్ ఎక్కడ ఉంది?", ml: "ഓട്ടോ സ്റ്റാൻഡ് എവിടെയാണ്?" },
    { id: "t2", cat: "travel", icon: "🚌", en: "Which bus goes to station?", hi: "स्टेशन जाने वाली बस कौन सी है?", ta: "நிலையத்திற்கு செல்லும் பேருந்து எது?", kn: "ನಿಲ್ದಾಣಕ್ಕೆ ಹೋಗುವ ಬಸ್ ಯಾವುದು?", bn: "স্টেশনে কোন বাস যাবে?", te: "స్టేషన్ కు వెళ్లే బస్సు ఏది?", ml: "സ്റ്റേഷനിലേക്ക് പോകുന്ന ബസ് ഏതാണ്?" },
    { id: "t3", cat: "travel", icon: "🚶", en: "Help me cross the road", hi: "कृपया सड़क पार करा दीजिए", ta: "சாலையைக் கடக்க உதவுங்கள்", kn: "ರಸ್ತೆ ದಾಟಲು ಸಹಾಯ ಮಾಡಿ", bn: "রাস্তা পার হতে সাহায্য করুন", te: "రోడ్డు దాటడానికి సహాయం చేయండి", ml: "റോഡ് മുറിച്ചുകടക്കാൻ സഹായിക്കൂ" },
    { id: "t4", cat: "travel", icon: "🛑", en: "Please stop here", hi: "कृपया यहीं रोक दीजिए", ta: "தயவுசெய்து இங்கே நிறுத்துங்கள்", kn: "ದಯವಿಟ್ಟು ಇಲ್ಲಿ ನಿಲ್ಲಿಸಿ", bn: "দয়া করে এখানেই থামুন", te: "దయచేసి ఇక్కడే ఆపండి", ml: "ദയവായി ഇവിടെ നിർത്തൂ" },

    // Kirana & Money
    { id: "m1", cat: "shop", icon: "💰", en: "How much does this cost?", hi: "यह कितने का है?", ta: "இதன் விலை என்ன?", kn: "ಇದರ ಬೆಲೆ ಎಷ್ಟು?", bn: "এটার দাম কত?", te: "దీని ధర ఎంత?", ml: "ഇതിന് എത്ര വിലയാകും?" },
    { id: "m2", cat: "shop", icon: "📱", en: "I will pay with UPI QR code", hi: "मैं यूपीआई से भुगतान करूँगा", ta: "நான் UPI மூலம் செலுத்துகிறேன்", kn: "ನಾನು ಯುಪಿಐ ಮೂಲಕ ಹಣ ಪಾವತಿಸುತ್ತೇನೆ", bn: "আমি UPI দিয়ে টাকা দেব", te: "నేను UPI ద్వారా చెల్లిస్తాను", ml: "ഞാൻ യുപിഐ വഴി പണം നൽകാം" },
    { id: "m3", cat: "shop", icon: "💵", en: "Please check this currency note", hi: "कृपया यह नोट जाँच लीजिए", ta: "இந்த ரூபாய் நோட்டை சரிபார்க்கவும்", kn: "ದಯವಿಟ್ಟು ಈ ನೋಟನ್ನು ಪರಿಶೀಲಿಸಿ", bn: "দয়া করে এই নোটটি দেখে দিন", te: "దయచేసి ఈ నోటును పరిశీలించండి", ml: "ദയവായി ഈ നോട്ട് പരിശോധിക്കൂ" },
    { id: "m4", cat: "shop", icon: "🧾", en: "Please give the bill", hi: "कृपया रसीद दीजिए", ta: "ரசீது கொடுங்கள்", kn: "ದಯವಿಟ್ಟು ರಶೀದಿ ಕೊಡಿ", bn: "দয়া করে রসিদ দিন", te: "దయచేసి బిల్లు ఇవ్వండి", ml: "ദയവായി രസീത് തരൂ" },

    // Daily Needs & Food
    { id: "d1", cat: "daily", icon: "💧", en: "I need drinking water", hi: "मुझे पीने का पानी चाहिए", ta: "எனக்கு குடிநீர் வேண்டும்", kn: "ನನಗೆ ಕುಡಿಯಲು ನೀರು ಬೇಕು", bn: "আমার খাবার জল চাই", te: "నాకు తాగడానికి నీరు కావాలి", ml: "എനിക്ക് കുടിവെള്ളം വേണം" },
    { id: "d2", cat: "daily", icon: "🍚", en: "I am hungry, need food", hi: "मुझे भूख लगी है, खाना चाहिए", ta: "எனக்கு பசிக்கிறது, உணவு வேண்டும்", kn: "ನನಗೆ ಹಸಿವಾಗಿದೆ, ಊಟ ಬೇಕು", bn: "আমার খিদে পেয়েছে, খাবার চাই", te: "నాకు ఆకలిగా ఉంది, ఆహారం కావాలి", ml: "എനിക്ക് വിശക്കുന്നു, ഭക്ഷണം വേണം" },
    { id: "d3", cat: "daily", icon: "🚻", en: "Where is the washroom?", hi: "शौचालय कहाँ पर है?", ta: "கழிப்பறை எங்கே உள்ளது?", kn: "ಶೌಚಾಲಯ ಎಲ್ಲಿದೆ?", bn: "শৌচাগার কোথায়?", te: "మరుగుదొడ్డి ఎక్కడ ఉంది?", ml: "ശുചിമുറി എവിടെയാണ്?" },
    { id: "d4", cat: "daily", icon: "😴", en: "I need to rest", hi: "मुझे आराम करना है", ta: "நான் ஓய்வெடுக்க வேண்டும்", kn: "ನಾನು ವಿಶ್ರಾಂತಿ ಪಡೆಯಬೇಕು", bn: "আমার একটু বিশ্রাম দরকার", te: "నేను విశ్రాంతి తీసుకోవాలి", ml: "എനിക്ക് വിശ്രമിക്കണം" },

    // Courtesy & Polite
    { id: "p1", cat: "polite", icon: "🙏", en: "Namaste / Greetings", hi: "नमस्ते", ta: "வணக்கம்", kn: "ನಮಸ್ಕಾರ", bn: "নমস্কার", te: "నమస్కారం", ml: "നമസ്കാരം" },
    { id: "p2", cat: "polite", icon: "💐", en: "Thank you very much", hi: "बहुत-बहुत धन्यवाद", ta: "மிக்க நன்றி", kn: "ತುಂಬಾ ಧನ್ಯವಾದಗಳು", bn: "অনেক ধন্যবাদ", te: "చాలా ధన్యవాదాలు", ml: "വളരെ നന്ദി" },
    { id: "p3", cat: "polite", icon: "👍", en: "Yes, I agree", hi: "हाँ, ठीक है", ta: "ஆம், சரி", kn: "ಹೌದು, ಸರಿ", bn: "হ্যাঁ, ঠিক আছে", te: "అవును, సరే", ml: "അതെ, ശരി" },
    { id: "p4", cat: "polite", icon: "👎", en: "No, thank you", hi: "नहीं, धन्यवाद", ta: "இல்லை, நன்றி", kn: "ಇಲ್ಲ, ಧನ್ಯವಾದ", bn: "না, ধন্যবাদ", te: "వద్దు, ధన్యవాదాలు", ml: "വേണ്ട, നന്ദി" }
  ];

  let currentAacFilter = "all";

  function initAacModule() {
    renderAacGrid();

    // Category filter pills
    document.querySelectorAll(".aac-category-filter .cat-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".aac-category-filter .cat-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentAacFilter = btn.dataset.cat || "all";
        renderAacGrid();
        hapticBuzz(30);
      });
    });

    $("btn-aac-speak").addEventListener("click", () => {
      if (sentence.length === 0) {
        speakText("Sentence is empty. Tap tiles below to construct words.");
        return;
      }
      const fullText = sentence.map(s => s.text).join(". ");
      speakText(fullText);
      hapticBuzz(50);
    });

    $("btn-aac-undo").addEventListener("click", () => {
      if (sentence.length > 0) {
        sentence.pop();
        updateSentenceDisplay();
        hapticBuzz(25);
      }
    });

    $("btn-aac-clear").addEventListener("click", () => {
      sentence = [];
      updateSentenceDisplay();
      stopSpeech();
      hapticBuzz(35);
    });

    $("btn-aac-speak-custom").addEventListener("click", () => {
      const val = $("aac-custom-input").value.trim();
      if (val) {
        speakText(val);
        hapticBuzz(40);
      }
    });

    $("aac-custom-input").addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        $("btn-aac-speak-custom").click();
      }
    });
  }

  function renderAacGrid() {
    const grid = $("aac-tiles-grid");
    if (!grid) return;
    grid.innerHTML = "";

    const langKey = currentLang.slice(0, 2);

    const filtered = AAC_DATA.filter(item => {
      return currentAacFilter === "all" || item.cat === currentAacFilter;
    });

    filtered.forEach(item => {
      const label = item[langKey] || item.hi || item.en;
      const tile = document.createElement("button");
      tile.className = "aac-tile";
      tile.setAttribute("aria-label", `${item.en}, speaks ${label}`);
      tile.innerHTML = `
        <span class="tile-icon" aria-hidden="true">${item.icon}</span>
        <span class="tile-label">${label}</span>
      `;

      tile.addEventListener("click", () => {
        hapticBuzz(40);
        sentence.push({ text: label, icon: item.icon });
        updateSentenceDisplay();
        speakText(label, 0.95);
      });

      grid.appendChild(tile);
    });
  }

  function updateSentenceDisplay() {
    const box = $("aac-sentence-box");
    if (sentence.length === 0) {
      box.innerHTML = `<span style="opacity: 0.6; font-size: 1rem;">(Constructed sentence will appear here)</span>`;
      return;
    }
    box.innerHTML = sentence.map(s => `<span style="background:var(--surface); border:1px solid var(--border); padding:4px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:4px;">${s.icon} ${s.text}</span>`).join(" ");
  }

  // --- 8. MODULE 4: SAFER JOURNEY & INDIAN STREET MOBILITY ---
  const STREET_HAZARDS = {
    pothole: {
      title: "Warning: Pothole / Broken Slab Ahead",
      desc: "Deep uneven pothole 1.5 meters ahead. Keep slightly to the left.",
      icon: "⚠️",
      haptic: [250, 100, 250],
      isDanger: true,
      audioFreq: 500
    },
    drain: {
      title: "Danger: Open Storm Drain (Nala) on Right",
      desc: "Uncovered drain slab detected 1 meter to the right. Step carefully left.",
      icon: "🚨",
      haptic: [300, 80, 300, 80, 500],
      isDanger: true,
      audioFreq: 880
    },
    cable: {
      title: "Caution: Low Hanging Electrical Wire / Cable",
      desc: "Overhead wire hanging at chest/head height 2 meters ahead.",
      icon: "⚡",
      haptic: [400, 150, 400],
      isDanger: true,
      audioFreq: 650
    },
    cattle: {
      title: "Caution: Stray Cattle on Pedestrian Path",
      desc: "Large stationary animal detected 3 meters ahead on the footpath.",
      icon: "🐄",
      haptic: [200, 100, 200],
      isDanger: false,
      audioFreq: 400
    },
    clear: {
      title: "Path Status: Clear",
      desc: "No immediate open drains or low hanging cables detected.",
      icon: "🟢",
      haptic: [60],
      isDanger: false,
      audioFreq: 0
    }
  };

  function initJourneyModule() {
    const banner = $("journey-hazard-banner");
    const bannerIcon = $("journey-banner-icon");
    const bannerTitle = $("journey-banner-title");
    const bannerDesc = $("journey-banner-desc");
    const simText = $("journey-sim-text");
    const simIcon = $("journey-sim-icon");

    function applyHazard(key) {
      const h = STREET_HAZARDS[key];
      if (!h) return;

      bannerIcon.textContent = h.icon;
      bannerTitle.textContent = h.title;
      bannerDesc.textContent = h.desc;
      simText.textContent = h.title;
      simIcon.textContent = h.icon;

      if (h.isDanger) {
        banner.className = "hazard-alert-banner";
        triggerScreenStrobe();
        if (h.audioFreq > 0) playAudioTone(h.audioFreq, 500, "sawtooth");
      } else {
        banner.className = "hazard-alert-banner safe";
      }

      hapticBuzz(h.haptic);
      speakText(`${h.title}. ${h.desc}`);
    }

    $("btn-sim-pothole").addEventListener("click", () => applyHazard("pothole"));
    $("btn-sim-drain").addEventListener("click", () => applyHazard("drain"));
    $("btn-sim-cable").addEventListener("click", () => applyHazard("cable"));
    $("btn-sim-cattle").addEventListener("click", () => applyHazard("cattle"));
    $("btn-sim-clear").addEventListener("click", () => applyHazard("clear"));

    // SOS Beacon Trigger
    $("btn-trigger-sos").addEventListener("click", () => {
      triggerScreenStrobe();
      hapticBuzz([150, 50, 150, 50, 150, 200, 400, 100, 400, 100, 400, 200, 150, 50, 150, 50, 150]);
      playAudioTone(1000, 1200, "square");
      speakText("Emergency SOS beacon activated! Sending location alerts.", 1.1);
      guideVoice("Emergency SOS beacon sounding.");
    });

    // Geolocation Share
    $("btn-share-location").addEventListener("click", () => {
      const geoStatus = $("journey-geo-status");
      if (!navigator.geolocation) {
        geoStatus.textContent = "Geolocation is not supported by your browser.";
        return;
      }
      geoStatus.textContent = "Fetching current GPS coordinates...";
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          const lat = pos.coords.latitude.toFixed(5);
          const lon = pos.coords.longitude.toFixed(5);
          const mapsUrl = `https://maps.google.com/?q=${lat},${lon}`;
          const message = encodeURIComponent(`EMERGENCY: I need assistance. My current GPS location in India is: ${mapsUrl}`);
          const waUrl = `https://wa.me/?text=${message}`;
          geoStatus.innerHTML = `GPS Acquired: ${lat}, ${lon} <br><a href="${waUrl}" target="_blank" rel="noopener" class="cat-btn" style="display:inline-block; margin-top:6px; background:var(--primary); color:#fff;">📲 Send on WhatsApp</a>`;
          hapticBuzz([100, 50, 100]);
          speakText(`Location retrieved. Ready to share via WhatsApp.`);
        },
        (err) => {
          // Fallback with mock Indian coordinates if denied
          const mockLat = "28.6139", mockLon = "77.2090"; // New Delhi
          const mapsUrl = `https://maps.google.com/?q=${mockLat},${mockLon}`;
          const message = encodeURIComponent(`EMERGENCY: I need assistance. My location: ${mapsUrl}`);
          const waUrl = `https://wa.me/?text=${message}`;
          geoStatus.innerHTML = `Location permission pending. Quick link: <a href="${waUrl}" target="_blank" rel="noopener" class="cat-btn" style="display:inline-block; margin-top:6px; background:var(--primary); color:#fff;">📲 Open WhatsApp SOS</a>`;
        },
        { enableHighAccuracy: true, timeout: 6000 }
      );
    });
  }

  // Visual strobe helper
  function triggerScreenStrobe() {
    document.body.classList.add("screen-flash");
    setTimeout(() => {
      document.body.classList.remove("screen-flash");
    }, 1200);
  }

  // --- 9. MODULE 5: INDIAN SIGN LANGUAGE (ISL) STUDIO ---
  const ISL_DICTIONARY = [
    // Alphabet
    { id: "isl-a", cat: "alphabet", name: "Letter A", desc: "Two-handed ISL: Left hand open palm up, right index touches tip of left thumb.", svg: createHandSvg("A") },
    { id: "isl-b", cat: "alphabet", name: "Letter B", desc: "Two-handed ISL: Both index fingers and thumbs form two circles touching vertically.", svg: createHandSvg("B") },
    { id: "isl-c", cat: "alphabet", name: "Letter C", desc: "Right hand curved in a half circle (C-shape) facing left.", svg: createHandSvg("C") },
    { id: "isl-d", cat: "alphabet", name: "Letter D", desc: "Right index pointing up, thumb and middle finger touch to form circle base.", svg: createHandSvg("D") },
    { id: "isl-e", cat: "alphabet", name: "Letter E", desc: "Left open palm, right index touches tip of left index finger.", svg: createHandSvg("E") },

    // Numbers
    { id: "isl-1", cat: "numbers", name: "Number 1 (एक)", desc: "Right index finger pointed upwards, other fingers closed in fist.", svg: createHandSvg("1") },
    { id: "isl-2", cat: "numbers", name: "Number 2 (दो)", desc: "Right index and middle finger pointing up in V-shape.", svg: createHandSvg("2") },
    { id: "isl-3", cat: "numbers", name: "Number 3 (तीन)", desc: "Right thumb, index and middle fingers extended.", svg: createHandSvg("3") },
    { id: "isl-5", cat: "numbers", name: "Number 5 (पाँच)", desc: "Open palm facing forward with all 5 fingers spread.", svg: createHandSvg("5") },
    { id: "isl-10", cat: "numbers", name: "Number 10 (दस)", desc: "Two open palms held up together showing 10 fingers, or shaking thumb up.", svg: createHandSvg("10") },

    // Daily Greetings
    { id: "isl-namaste", cat: "daily", name: "Namaste (नमस्ते)", desc: "Both palms joined together in front of chest with a slight respectful head nod.", svg: createHandSvg("🙏") },
    { id: "isl-thankyou", cat: "daily", name: "Thank You (धन्यवाद)", desc: "Fingertips of right hand touch lips/chin and move outwards forward with open palm.", svg: createHandSvg("💐") },
    { id: "isl-yes", cat: "daily", name: "Yes (हाँ)", desc: "Closed right fist nodding up and down like a head nod.", svg: createHandSvg("👍") },
    { id: "isl-no", cat: "daily", name: "No (नहीं)", desc: "Index and middle fingers snap together against thumb twice, or side shake.", svg: createHandSvg("👎") },
    { id: "isl-water", cat: "daily", name: "Water (पानी)", desc: "W-hand shape near mouth, or cupped hand moving to mouth as drinking.", svg: createHandSvg("💧") },
    { id: "isl-food", cat: "daily", name: "Food / Eat (खाना)", desc: "Fingertips bunched together tapping lips twice.", svg: createHandSvg("🍚") },

    // School
    { id: "isl-school", cat: "school", name: "School (विद्यालय)", desc: "Right flat palm claps on left flat palm twice horizontally.", svg: createHandSvg("🏫") },
    { id: "isl-teacher", cat: "school", name: "Teacher (अध्यापक)", desc: "Both hands pinch at forehead, move forward opening into flat palms downwards.", svg: createHandSvg("👨‍🏫") },
    { id: "isl-book", cat: "school", name: "Book / Read (किताब)", desc: "Both flat palms pressed together then opened outwards like a book cover.", svg: createHandSvg("📖") },
    { id: "isl-write", cat: "school", name: "Write (लिखना)", desc: "Right thumb and index mimic holding a pen and writing across flat left palm.", svg: createHandSvg("✍️") },

    // Emergency
    { id: "isl-help", cat: "emergency", name: "Help (सहायता)", desc: "Left flat palm facing up, right closed fist with thumb up placed on left palm, moving upward together.", svg: createHandSvg("🆘") },
    { id: "isl-doctor", cat: "emergency", name: "Doctor (डॉक्टर)", desc: "Right index and middle fingertips tap inner pulse point of left wrist.", svg: createHandSvg("🩺") },
    { id: "isl-medicine", cat: "emergency", name: "Medicine (दवा)", desc: "Right middle finger grinds in the center of open left palm like crushing a tablet.", svg: createHandSvg("💊") },
    { id: "isl-danger", cat: "emergency", name: "Danger / Stop (खतरा)", desc: "Firm open right hand thrust forward vertically in an abrupt stopping gesture.", svg: createHandSvg("🛑") }
  ];

  function createHandSvg(symbol) {
    return `
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ISL gesture ${symbol}">
        <circle cx="50" cy="50" r="44" fill="#e0f2f1" stroke="#00796b" stroke-width="3"/>
        <text x="50" y="62" font-size="34" font-weight="bold" fill="#004d40" text-anchor="middle" font-family="sans-serif">${symbol}</text>
      </svg>
    `;
  }

  let activeIslCat = "alphabet";

  function initIslModule() {
    renderIslCards();

    document.querySelectorAll(".aac-category-filter [data-isl-cat]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".aac-category-filter [data-isl-cat]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeIslCat = btn.dataset.islCat || "alphabet";
        renderIslCards();
        hapticBuzz(30);
      });
    });

    $("btn-new-isl-quiz").addEventListener("click", () => {
      renderIslQuiz();
      hapticBuzz(35);
    });

    renderIslQuiz();
  }

  function renderIslCards() {
    const grid = $("isl-cards-grid");
    if (!grid) return;
    grid.innerHTML = "";

    const items = ISL_DICTIONARY.filter(i => i.cat === activeIslCat);
    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "isl-card";
      card.innerHTML = `
        <div class="isl-svg-box">${item.svg}</div>
        <div class="isl-name">${item.name}</div>
        <div class="isl-desc">${item.desc}</div>
        <button class="btn-primary" style="margin-top:auto; width:100%; min-height:40px; font-size:0.85rem;">🔊 Listen & Practice</button>
      `;

      card.querySelector("button").addEventListener("click", () => {
        speakText(`${item.name}. ${item.desc}`);
        hapticBuzz([80, 50, 80]);
      });

      grid.appendChild(card);
    });
  }

  function filterISLBySearch(term) {
    activeIslCat = "daily";
    document.querySelectorAll(".aac-category-filter [data-isl-cat]").forEach(b => {
      b.classList.toggle("active", b.dataset.islCat === "daily");
    });
    renderIslCards();
    speakText(`Showing Indian Sign Language for ${term}`);
  }

  function renderIslQuiz() {
    const box = $("isl-quiz-box");
    const feedback = $("isl-quiz-feedback");
    feedback.textContent = "";

    // Pick 1 random question item and 2 distractors
    const pool = ISL_DICTIONARY.filter(i => i.cat !== "alphabet");
    const target = pool[Math.floor(Math.random() * pool.length)];
    const distractors = pool.filter(i => i.id !== target.id).sort(() => 0.5 - Math.random()).slice(0, 2);
    const options = [target, ...distractors].sort(() => 0.5 - Math.random());

    let html = `
      <div style="text-align:center; margin-bottom:12px;">
        <p style="font-weight:700;">Which gesture means:</p>
        <div style="font-size:1.4rem; font-weight:900; color:var(--primary); margin:6px 0;">"${target.name}"</div>
        <p style="font-size:0.9rem; color:var(--fg-muted);">${target.desc}</p>
      </div>
      <div class="quiz-options">
    `;

    options.forEach((opt, idx) => {
      html += `<button class="quiz-opt-btn" data-sign-id="${opt.id}" style="display:flex; align-items:center; gap:10px;">
        <span style="width:40px; height:40px; display:inline-block;">${opt.svg}</span>
        <strong>${opt.name}</strong>
      </button>`;
    });

    html += `</div>`;
    box.innerHTML = html;

    box.querySelectorAll(".quiz-opt-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const pickedId = btn.dataset.signId;
        if (pickedId === target.id) {
          btn.classList.add("correct");
          feedback.textContent = "🎉 Correct! That is the verified ISL sign.";
          feedback.style.color = "var(--success)";
          hapticBuzz([100, 50, 100]);
          speakText("Correct answer! Good job.");
        } else {
          btn.classList.add("incorrect");
          feedback.textContent = `❌ That was not it. The correct sign is: ${target.name}`;
          feedback.style.color = "var(--danger)";
          hapticBuzz([300, 100]);
          speakText(`Incorrect. The correct sign is ${target.name}`);
        }
      });
    });
  }

  // --- 10. MODULE 6: MULTISENSORY SOUND SENTINEL & DEAFBLIND ENGINE ---
  let soundAudioContext = null;
  let micMediaStream = null;
  let soundMonitorInterval = null;

  function initAlertsModule() {
    const toggleBtn = $("btn-toggle-sound-alert");
    const thresholdInput = $("alert-threshold");
    const thresholdVal = $("threshold-val");
    const statusText = $("sound-alert-status");

    thresholdInput.addEventListener("input", () => {
      thresholdVal.textContent = thresholdInput.value;
    });

    $("btn-test-strobe").addEventListener("click", () => {
      triggerScreenStrobe();
      hapticBuzz([200, 80, 200]);
      guideVoice("Screen strobe flash test executed.");
    });

    toggleBtn.addEventListener("click", async () => {
      if (soundMonitorInterval) {
        // Stop listener
        clearInterval(soundMonitorInterval);
        soundMonitorInterval = null;
        if (micMediaStream) {
          micMediaStream.getTracks().forEach(t => t.stop());
          micMediaStream = null;
        }
        toggleBtn.textContent = "🎙️ Start Sound Sentinel";
        statusText.textContent = "Sound sentinel is stopped.";
        hapticBuzz(35);
        return;
      }

      try {
        micMediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        soundAudioContext = new AudioCtx();
        const analyser = soundAudioContext.createAnalyser();
        analyser.fftSize = 512;

        const source = soundAudioContext.createMediaStreamSource(micMediaStream);
        source.connect(analyser);

        const dataArray = new Uint8Array(analyser.fftSize);
        let lastTriggerTime = 0;

        soundMonitorInterval = setInterval(() => {
          analyser.getByteTimeDomainData(dataArray);
          let sumSquares = 0;
          for (let i = 0; i < dataArray.length; i++) {
            const dev = dataArray[i] - 128;
            sumSquares += dev * dev;
          }
          const rms = Math.sqrt(sumSquares / dataArray.length);
          const limit = parseInt(thresholdInput.value, 10) / 2;

          if (rms > limit && Date.now() - lastTriggerTime > 2500) {
            lastTriggerTime = Date.now();
            triggerScreenStrobe();
            hapticBuzz([350, 100, 350, 100, 500]);
            statusText.textContent = `🚨 LOUD SOUND DETECTED at ${new Date().toLocaleTimeString()} (Horn / Doorbell / Shouting)`;
            statusText.style.color = "var(--danger)";
            playAudioTone(950, 400, "square");
          }
        }, 100);

        toggleBtn.textContent = "⏹️ Stop Sound Sentinel";
        statusText.textContent = "Active: Monitoring for sudden horns, sirens, or doorbells...";
        statusText.style.color = "var(--success)";
        hapticBuzz([80, 40, 80]);
      } catch (err) {
        statusText.textContent = "Microphone access blocked. Please allow mic in browser settings.";
        statusText.style.color = "var(--danger)";
      }
    });

    // Deafblind Tactile Pad Engine
    const tactileStatus = $("tactile-status");

    $("btn-tactile-yes").addEventListener("click", () => {
      // YES: Gentle double pulse
      hapticBuzz([120, 80, 120]);
      tactileStatus.textContent = "Tactile Signal: YES (Double Short Pulse)";
      guideVoice("Yes");
    });

    $("btn-tactile-no").addEventListener("click", () => {
      // NO: Long heavy double buzz
      hapticBuzz([450, 150, 450]);
      tactileStatus.textContent = "Tactile Signal: NO (Two Long Pulses)";
      guideVoice("No");
    });

    $("btn-tactile-danger").addEventListener("click", () => {
      // DANGER / STOP: Staccato alarm pulse
      hapticBuzz([100, 50, 100, 50, 100, 50, 100, 50, 400]);
      triggerScreenStrobe();
      tactileStatus.textContent = "Tactile Signal: DANGER / STOP (Rapid Staccato Vibration)";
      guideVoice("Danger. Stop.");
    });

    $("btn-test-sos-morse").addEventListener("click", () => {
      // Morse SOS: ... --- ...
      hapticBuzz([100, 100, 100, 100, 100, 300, 300, 100, 300, 100, 300, 300, 100, 100, 100, 100, 100]);
      tactileStatus.textContent = "Vibrating Morse SOS: ••• --- ••• (3 short, 3 long, 3 short)";
      guideVoice("Vibrating SOS Morse Code");
    });

    $("btn-test-doorbell-haptic").addEventListener("click", () => {
      hapticBuzz([200, 100, 400]);
      tactileStatus.textContent = "Vibrating Doorbell Chime: Ding-Dong Rhythm";
      guideVoice("Doorbell tactile rhythm");
    });
  }

  // --- 11. MODULE 7: RUPEE CURRENCY & MEDICINE IDENTIFIER ---
  const CURRENCY_DATABASE = {
    "10": {
      name: "₹10 Banknote",
      series: "Mahatma Gandhi (New) Series",
      color: "Chocolate Brown",
      motif: "Sun Temple, Konark",
      pulses: [150],
      checklist: [
        "Tactile: Geometric shape on right for visually impaired.",
        "Front: Portrait of Mahatma Gandhi at center.",
        "Back: Motif of Sun Temple, Konark wheel.",
        "Color: Chocolate brown with microlettering 'RBI' and '10'."
      ]
    },
    "20": {
      name: "₹20 Banknote",
      series: "Mahatma Gandhi (New) Series",
      color: "Greenish Yellow",
      motif: "Ellora Caves",
      pulses: [150, 100, 150],
      checklist: [
        "Tactile: Distinctive raised numeral '20' on right.",
        "Color: Vibrant greenish-yellow.",
        "Back: Ellora Caves depicting Indian heritage.",
        "Windowed demetalised security thread with inscriptions 'भारत' and 'RBI'."
      ]
    },
    "50": {
      name: "₹50 Banknote",
      series: "Mahatma Gandhi (New) Series",
      color: "Fluorescent Blue",
      motif: "Hampi with Chariot",
      pulses: [150, 80, 150, 80, 150],
      checklist: [
        "Tactile: Square symbol above Ashoka Pillar emblem.",
        "Back: Motif of Hampi with Chariot.",
        "Color: Distinct Fluorescent Blue.",
        "Ashoka Pillar emblem on the right side."
      ]
    },
    "100": {
      name: "₹100 Banknote",
      series: "Mahatma Gandhi (New) Series",
      color: "Lavender",
      motif: "Rani ki Vav (Queen's Stepwell)",
      pulses: [200, 80, 200, 80, 200, 80, 200],
      checklist: [
        "Tactile: Triangle mark on right & 4 angular bleed lines on left and right borders.",
        "Back: Motif of Rani ki Vav, Gujarat.",
        "Color: Lavender shade.",
        "Color-shifting security thread: color shifts from green to blue when tilted."
      ]
    },
    "200": {
      name: "₹200 Banknote",
      series: "Mahatma Gandhi (New) Series",
      color: "Bright Yellow",
      motif: "Sanchi Stupa",
      pulses: [250, 80, 250, 80, 250],
      checklist: [
        "Tactile: H-mark with two small circles & 4 bleed lines with two small circles in between.",
        "Back: Motif of Sanchi Stupa.",
        "Color: Bright Yellow.",
        "Latent image of 200 visible when tilted at eye level."
      ]
    },
    "500": {
      name: "₹500 Banknote",
      series: "Mahatma Gandhi (New) Series",
      color: "Stone Grey",
      motif: "Red Fort, Delhi",
      pulses: [300, 80, 300, 80, 300, 80, 300, 80, 300],
      checklist: [
        "Tactile: Circle mark on right & 5 angular bleed lines on both sides.",
        "Security Thread: Changes from green to blue with 'भारत' and 'RBI'.",
        "Back: Motif of Red Fort with Indian tricolour flag.",
        "Electrotype Mahatma Gandhi watermark visible when viewed against light."
      ]
    },
    "coin5": {
      name: "₹5 Indian Coin",
      series: "New Series with Rupee Symbol",
      color: "Nickel-Brass / Stainless Steel",
      motif: "Lion Capital & Numeral 5",
      pulses: [100, 50, 100],
      checklist: [
        "Diameter: 23mm, Circular shape with milled edge.",
        "Tactile: Raised numeral 5 in center with rupee symbol ₹.",
        "Obverse: Lion Capital of Ashoka Pillar with 'Satyameva Jayate'."
      ]
    },
    "coin10": {
      name: "₹10 Bimetallic Coin",
      series: "Bimetallic Coin Series",
      color: "Two-tone: Nickel-bronze center with Aluminium-bronze ring",
      motif: "10 rays / Connecting notches",
      pulses: [150, 60, 150, 60, 150],
      checklist: [
        "Design: Bimetallic composition with raised concentric ring.",
        "Diameter: 27mm with smooth plain edge.",
        "Tactile: Distinct double-metal boundary felt by touch."
      ]
    },
    "coin20": {
      name: "₹20 Dodecagonal Coin",
      series: "12-Sided Coin Series for Visually Impaired",
      color: "Bimetallic 12-sided polygon",
      motif: "Grains motif symbolizing agriculture",
      pulses: [200, 50, 200, 50, 200, 50, 200],
      checklist: [
        "Shape: 12-sided polygon (Dodecagon) specifically designed for blind users.",
        "Tactile: 12 distinct corners easily identifiable by touch.",
        "Center: Nickel-brass core with Nickel-silver outer ring."
      ]
    }
  };

  const MEDICINES_DATA = {
    pcm: {
      name: "Paracetamol 500 mg",
      desc: "Used to treat fever and mild-to-moderate body pain.",
      dose: "Take 1 tablet every 6 to 8 hours after food. Do not exceed 4 tablets in 24 hours.",
      caution: "Caution: Avoid taking with other paracetamol products. Overuse damages liver."
    },
    met: {
      name: "Metformin 500 mg",
      desc: "Oral medicine for type-2 diabetes blood sugar management.",
      dose: "Take 1 tablet once or twice daily with meals to avoid stomach upset.",
      caution: "Caution: Do not skip meals after taking this medicine. Store in cool, dry place."
    },
    amox: {
      name: "Amoxicillin 250 mg",
      desc: "Antibiotic used to treat bacterial throat, ear, and chest infections.",
      dose: "Take 1 capsule 3 times a day at regular 8-hour intervals.",
      caution: "Important: Complete the full 5-day course even if you feel better."
    },
    ors: {
      name: "Oral Rehydration Salts (ORS Electral)",
      desc: "Restores body water and essential electrolytes lost due to dehydration or diarrhea.",
      dose: "Mix 1 full packet in exactly 1 litre of clean drinking water. Drink throughout the day.",
      caution: "Notice: Do not boil the prepared solution. Discard after 24 hours."
    },
    cough: {
      name: "Ayurvedic Herbal Cough Syrup",
      desc: "Relieves dry cough, sore throat, and chest congestion.",
      dose: "Take 2 teaspoonfuls (10 ml) 3 times a day with warm water.",
      caution: "Shake bottle well before use. Keep cap tightly closed."
    }
  };

  let activeCurrency = CURRENCY_DATABASE["500"];

  function initCurrencyModule() {
    const badge = $("currency-denomination-badge");
    const details = $("currency-details");
    const checklistUl = $("currency-checklist");

    function renderActiveCurrency() {
      badge.textContent = activeCurrency.name;
      details.textContent = `${activeCurrency.series} • ${activeCurrency.color} • ${activeCurrency.motif}`;

      checklistUl.innerHTML = "";
      activeCurrency.checklist.forEach(item => {
        const li = document.createElement("li");
        li.textContent = `✅ ${item}`;
        checklistUl.appendChild(li);
      });
    }

    renderActiveCurrency();

    document.querySelectorAll(".btn-curr-pick").forEach(btn => {
      btn.addEventListener("click", () => {
        const val = btn.dataset.val;
        activeCurrency = CURRENCY_DATABASE[val];
        renderActiveCurrency();
        hapticBuzz(activeCurrency.pulses);
        speakText(`${activeCurrency.name}. ${activeCurrency.color}. ${activeCurrency.motif}`);
      });
    });

    $("btn-speak-currency").addEventListener("click", () => {
      speakText(`${activeCurrency.name}. Series: ${activeCurrency.series}. Color: ${activeCurrency.color}. Key motif: ${activeCurrency.motif}. Check security features.`);
    });

    $("btn-tactile-currency").addEventListener("click", () => {
      hapticBuzz(activeCurrency.pulses);
      guideVoice(`Emitting tactile pulse pattern for ${activeCurrency.name}`);
    });

    // Medicine Reader
    const medSelect = $("medicine-select");
    const medName = $("med-name");
    const medInst = $("med-instructions");
    const medCaution = $("med-caution");

    function updateMedicine() {
      const key = medSelect.value;
      const m = MEDICINES_DATA[key];
      if (m) {
        medName.textContent = m.name;
        medInst.textContent = `${m.desc} ${m.dose}`;
        medCaution.textContent = m.caution;
      }
    }

    medSelect.addEventListener("change", updateMedicine);
    updateMedicine();

    $("btn-read-medicine").addEventListener("click", () => {
      const m = MEDICINES_DATA[medSelect.value];
      speakText(`${m.name}. ${m.desc}. Dosage: ${m.dose}. ${m.caution}`);
      hapticBuzz([120, 60, 120]);
    });

    $("btn-schedule-med").addEventListener("click", () => {
      const m = MEDICINES_DATA[medSelect.value];
      hapticBuzz([200, 100, 200, 100, 300]);
      triggerScreenStrobe();
      speakText(`Dose reminder scheduled for ${m.name}. Alarm will sound and vibrate twice daily.`);
      guideVoice("Medicine dose reminder registered.");
    });
  }

  // --- REAL-TIME AIML INTEGRATION ---
  function initAIMLIntegration() {
    if (!window.SahaayaAIML) return;
    window.SahaayaAIML.initModels();

    let journeyFacing = "environment";
    let islFacing = "user";

    // 1. Classroom Neural OCR
    const ocrFileInput = $("classroom-ocr-file");
    const runOcrBtn = $("btn-run-ocr");
    const ocrStatusBadge = $("ocr-status-badge");
    const classroomText = $("classroom-text");

    let uploadedImageSource = null;

    if (ocrFileInput) {
      ocrFileInput.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (file) {
          uploadedImageSource = file;
          ocrStatusBadge.textContent = `Selected: ${file.name} (${Math.round(file.size / 1024)} KB). Click "Run Neural OCR" to extract text.`;
          hapticBuzz(35);
        }
      });
    }

    if (runOcrBtn) {
      runOcrBtn.addEventListener("click", async () => {
        ocrStatusBadge.textContent = "⏳ Running Client-Side Optical Recognition...";
        hapticBuzz([60, 40, 60]);

        const source = uploadedImageSource || "https://images.openai.com/static-rsc-4/hLQKrAZLCbvXvuBaUe6o1lNEGmiO0_cviiQoTMN_aZsbxoJYmpePg7NQA0qYqw1AOW88E5l_C3U0XzLR2ATiMlFBUkxWic56hpf3PZIq5amdva7zOG8aWuJpH9Q0N_bGhZlaBJOqPsJqrXxj9LAkpLxnF4WCdieLkkefM1i4lXUt4YVa8gn0t403oaxNQHK5?purpose=inline";
        const result = await window.SahaayaAIML.performOCR(source, (msg) => {
          ocrStatusBadge.textContent = msg;
        });

        if (result.success && result.text) {
          classroomText.value = result.text;
          ocrStatusBadge.textContent = `✅ OCR Extraction Complete (${result.confidence}% confidence). Ready to read aloud.`;
          hapticBuzz([100, 50, 100]);
          speakText("Worksheet text extracted successfully via AI OCR. Ready to read aloud.");
        }
      });
    }

    // 2. Safer Journey Real-Time AI Camera Sensor
    const startJourneyBtn = $("btn-start-journey-ai");
    const stopJourneyBtn = $("btn-stop-journey-ai");
    const switchJourneyBtn = $("btn-switch-journey-cam");
    const journeyVideo = $("journey-video");
    const journeyCanvas = $("journey-overlay-canvas");
    const journeyBadge = $("journey-ai-badge");
    const journeyPlaceholder = $("journey-scene-sim");

    if (startJourneyBtn && journeyVideo) {
      startJourneyBtn.addEventListener("click", async () => {
        startJourneyBtn.disabled = true;
        startJourneyBtn.textContent = "Connecting Camera...";
        const res = await window.SahaayaAIML.startCamera(journeyVideo, journeyFacing);
        startJourneyBtn.disabled = false;
        startJourneyBtn.textContent = "📹 Camera Active";

        if (res.success) {
          if (journeyPlaceholder) journeyPlaceholder.style.display = "none";
          if (journeyBadge) {
            journeyBadge.className = "ai-live-badge";
            journeyBadge.innerHTML = `<span class="ai-pulse-dot"></span> AI VISION: RUNNING`;
          }
          $("journey-hazard-tag").textContent = "● AI SENSOR: REAL-TIME INFERENCE";

          window.SahaayaAIML.startObstacleDetection(journeyVideo, journeyCanvas, (hazards) => {
            const banner = $("journey-hazard-banner");
            const icon = $("journey-banner-icon");
            const title = $("journey-banner-title");
            const desc = $("journey-banner-desc");

            if (hazards.length === 0) {
              banner.className = "hazard-alert-banner safe";
              icon.textContent = "🟢";
              title.textContent = "Path Status: Clear";
              desc.textContent = "No immediate obstacles or drops in front camera view.";
            } else {
              const mainH = hazards[0];
              banner.className = mainH.isClose ? "hazard-alert-banner" : "hazard-alert-banner safe";
              icon.textContent = mainH.isClose ? "🚨" : "⚠️";
              title.textContent = `${mainH.label} (${mainH.score}%)`;
              desc.textContent = `Detected at ${mainH.position}. Keep safe distance.`;
            }
          });

          hapticBuzz([100, 50, 100]);
          speakText("Real-time AI camera obstacle sensor activated.");
        } else {
          startJourneyBtn.textContent = "📹 Start Real-Time AI Camera";
          alert("Could not access camera: " + res.error);
        }
      });
    }

    if (stopJourneyBtn) {
      stopJourneyBtn.addEventListener("click", () => {
        window.SahaayaAIML.stopCamera();
        if (journeyPlaceholder) journeyPlaceholder.style.display = "block";
        if (journeyBadge) {
          journeyBadge.className = "ai-live-badge off";
          journeyBadge.innerHTML = `<span class="ai-pulse-dot"></span> AI SENSOR: IDLE`;
        }
        if (startJourneyBtn) startJourneyBtn.textContent = "📹 Start Real-Time AI Camera";
        $("journey-hazard-tag").textContent = "● AI SENSOR: READY";
        hapticBuzz(35);
      });
    }

    if (switchJourneyBtn) {
      switchJourneyBtn.addEventListener("click", () => {
        journeyFacing = (journeyFacing === "environment") ? "user" : "environment";
        if (startJourneyBtn && startJourneyBtn.textContent.includes("Active")) {
          startJourneyBtn.click();
        }
        hapticBuzz(30);
      });
    }

    // 3. Indian Sign Language (ISL) Real-Time Gesture Tracker
    const startIslBtn = $("btn-start-isl-cam");
    const stopIslBtn = $("btn-stop-isl-cam");
    const switchIslBtn = $("btn-switch-isl-cam");
    const islVideo = $("isl-video");
    const islCanvas = $("isl-overlay-canvas");
    const islBadge = $("isl-ai-badge");
    const islPlaceholder = $("isl-scene-placeholder");
    const islNameEl = $("isl-current-name");
    const islConfEl = $("isl-current-conf");

    if (startIslBtn && islVideo) {
      startIslBtn.addEventListener("click", async () => {
        startIslBtn.disabled = true;
        startIslBtn.textContent = "Connecting Camera...";
        const res = await window.SahaayaAIML.startCamera(islVideo, islFacing);
        startIslBtn.disabled = false;
        startIslBtn.textContent = "📹 ISL Camera Active";

        if (res.success) {
          if (islPlaceholder) islPlaceholder.style.display = "none";
          if (islBadge) {
            islBadge.className = "ai-live-badge";
            islBadge.innerHTML = `<span class="ai-pulse-dot"></span> AI GESTURE TRACKER: ACTIVE`;
          }
          $("isl-hud-tag").textContent = "● HAND TRACKER: REAL-TIME";

          window.SahaayaAIML.startGestureRecognition(islVideo, islCanvas, (gesture) => {
            if (gesture) {
              islNameEl.textContent = gesture.name;
              islConfEl.textContent = `Confidence: ${gesture.confidence}% | Aspect: ${gesture.aspectRatio}`;
            }
          });

          hapticBuzz([100, 50, 100]);
          speakText("Real-time Indian Sign Language gesture tracking camera activated.");
        } else {
          startIslBtn.textContent = "📹 Start Real-Time ISL Tracker";
          alert("Could not access camera: " + res.error);
        }
      });
    }

    if (stopIslBtn) {
      stopIslBtn.addEventListener("click", () => {
        window.SahaayaAIML.stopCamera();
        if (islPlaceholder) islPlaceholder.style.display = "block";
        if (islBadge) {
          islBadge.className = "ai-live-badge off";
          islBadge.innerHTML = `<span class="ai-pulse-dot"></span> AI GESTURE MODEL: READY`;
        }
        if (startIslBtn) startIslBtn.textContent = "📹 Start Real-Time ISL Tracker";
        $("isl-hud-tag").textContent = "● HAND TRACKER: IDLE";
        hapticBuzz(35);
      });
    }

    if (switchIslBtn) {
      switchIslBtn.addEventListener("click", () => {
        islFacing = (islFacing === "user") ? "environment" : "user";
        if (startIslBtn && startIslBtn.textContent.includes("Active")) {
          startIslBtn.click();
        }
        hapticBuzz(30);
      });
    }

    // 4. Acoustic Spectrum Analyzer & Sound Sentinel
    const audioSpectrumCanvas = $("audio-spectrum-canvas");
    const audioFftEvent = $("audio-fft-event");
    const startAudioBtn = $("btn-toggle-sound-alert");

    if (startAudioBtn && audioSpectrumCanvas) {
      let isAudioRunning = false;
      startAudioBtn.addEventListener("click", async () => {
        if (isAudioRunning) {
          window.SahaayaAIML.stopAcousticAnalyzer();
          isAudioRunning = false;
          startAudioBtn.textContent = "🎙️ Start Live FFT Sound Sentinel";
          if (audioFftEvent) audioFftEvent.textContent = "Sound sentinel stopped.";
          hapticBuzz(35);
        } else {
          const res = await window.SahaayaAIML.startAcousticAnalyzer(audioSpectrumCanvas, (event) => {
            if (event && audioFftEvent) {
              audioFftEvent.textContent = `${event.name} (${event.freq} Hz)`;
              triggerScreenStrobe();
            }
          });
          if (res.success) {
            isAudioRunning = true;
            startAudioBtn.textContent = "⏹️ Stop FFT Sound Sentinel";
            if (audioFftEvent) audioFftEvent.textContent = "Active: Monitoring 60 FPS Spectrogram...";
            hapticBuzz([80, 40, 80]);
          }
        }
      });
    }

    // 5. Currency Real-Time Camera Scanner
    const startCurrCamBtn = $("btn-start-curr-cam");
    const snapCurrAiBtn = $("btn-snap-curr-ai");
    const stopCurrCamBtn = $("btn-stop-curr-cam");
    const currVideo = $("currency-video");
    const currPlaceholder = $("currency-cam-placeholder");
    const currBadge = $("curr-ai-badge");

    if (startCurrCamBtn && currVideo) {
      startCurrCamBtn.addEventListener("click", async () => {
        const res = await window.SahaayaAIML.startCamera(currVideo, "environment");
        if (res.success) {
          if (currPlaceholder) currPlaceholder.style.display = "none";
          if (currBadge) {
            currBadge.className = "ai-live-badge";
            currBadge.innerHTML = `<span class="ai-pulse-dot"></span> SCANNER: CAMERA STREAMING`;
          }
          $("currency-hud-tag").textContent = "● SCANNER: LIVE";
          hapticBuzz(40);
          speakText("Camera active. Align note or coin in the viewfinder and tap Run AI Classification.");
        }
      });
    }

    if (snapCurrAiBtn && currVideo) {
      snapCurrAiBtn.addEventListener("click", () => {
        const result = window.SahaayaAIML.classifyIndianCurrency(currVideo);
        if (result) {
          $("currency-denomination-badge").textContent = `${result.denomination} (${result.confidence}%)`;
          $("currency-details").textContent = result.details;
          hapticBuzz([120, 60, 120, 60, 180]);
          triggerScreenStrobe();
          speakText(`Identified ${result.denomination} with ${result.confidence}% confidence. ${result.details}`);
        }
      });
    }

    if (stopCurrCamBtn) {
      stopCurrCamBtn.addEventListener("click", () => {
        window.SahaayaAIML.stopCamera();
        if (currPlaceholder) currPlaceholder.style.display = "block";
        if (currBadge) {
          currBadge.className = "ai-live-badge off";
          currBadge.innerHTML = `<span class="ai-pulse-dot"></span> SCANNER: READY`;
        }
        $("currency-hud-tag").textContent = "● CAMERA: IDLE";
        hapticBuzz(35);
      });
    }
  }

  // --- 12. UPDATE LANGUAGE VIEWS & OFFLINE PWA ---
  function updateAllLanguageViews() {
    renderAacGrid();
    updateSentenceDisplay();
  }

  function initPwa() {
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js').then(reg => {
          console.log("Sahaaya AI Offline ServiceWorker registered:", reg.scope);
        }).catch(err => {
          console.log("ServiceWorker registration skipped:", err);
        });
      });
    }
  }

  // --- DOM READY BOOTSTRAP ---
  document.addEventListener("DOMContentLoaded", () => {
    initToolbar();
    initProfiles();
    initTabs();
    initClassroomModule();
    initCommModule();
    initAacModule();
    initJourneyModule();
    initIslModule();
    initAlertsModule();
    initCurrencyModule();
    initAIMLIntegration();
    initPwa();
    console.log("Sahaaya AI Prototype initialized with Real-Time AIML.");
  });

})();
