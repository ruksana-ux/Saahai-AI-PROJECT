"""
Sahaaya AI — Augmentative & Alternative Communication (AAC) Engine (Pure Python)
Multilingual Indian communication board with situation presets and 180-degree flip cards.
"""

from typing import Dict, List, Any


class SahaayaAACEngine:
    """
    100% Python AAC Engine designed for nonspeaking, speech-impaired, and deaf citizens.
    Features culturally relevant Indian communication situations and 180° flip dialogue cards.
    """

    SITUATIONS = {
        "🏥 Clinic / Hospital / Chemist": [
            {
                "en": "Hello Doctor, I have had high fever and headache for 2 days.",
                "hi": "नमस्ते डॉक्टर, मुझे दो दिन से तेज बुखार और सिरदर्द है।",
                "ta": "வணக்கம் டாக்டர், எனக்கு இரண்டு நாட்களாக அதிக காய்ச்சல் மற்றும் தலைவலி உள்ளது.",
                "te": "నమస్తే డాక్టర్, నాకు రెండు రోజులుగా తీవ్ర జ్వరం మరియు తలనొప్పి ఉంది.",
                "kn": "ನಮಸ್ತೆ ಡಾಕ್ಟರ್, ನನಗೆ ಎರಡು ದಿನಗಳಿಂದ ತೀವ್ರ ಜ್ವರ ಮತ್ತು ತಲೆನೋವು ಇದೆ."
            },
            {
                "en": "Should this medicine be taken before or after meals?",
                "hi": "क्या यह दवा खाने से पहले लेनी है या बाद में?",
                "ta": "இந்த மருந்தை உணவுக்கு முன் சாப்பிட வேண்டுமா அல்லது பின் சாப்பிட வேண்டுமா?",
                "te": "ఈ మందును భోజనానికి ముందు తీసుకోవాలా లేక తర్వాత తీసుకోవాలా?",
                "kn": "ಈ ಔಷಧವನ್ನು ಊಟಕ್ಕೆ ಮುಂಚೆ ತೆಗೆದುಕೊಳ್ಳಬೇಕೇ ಅಥವಾ ನಂತರವೇ?"
            },
            {
                "en": "Please write the instructions in big letters on this paper.",
                "hi": "कृपया कागज़ पर निर्देश बड़े अक्षरों में लिख दीजिए।",
                "ta": "தயவுசெய்து காகிதத்தில் பெரிய எழுத்துக்களில் எழுதவும்.",
                "te": "దయచేసి కాగితంపై పెద్ద అక్షరాలతో సూచనలు రాయండి.",
                "kn": "ದಯವಿಟ್ಟು ಕಾಗದದಲ್ಲಿ ದೊಡ್ಡ ಅಕ್ಷರಗಳಲ್ಲಿ ಬರೆದು ಕೊಡಿ."
            },
            {
                "en": "I am scared of injections, is an oral syrup or tablet available?",
                "hi": "मुझे इंजेक्शन से डर लगता है, क्या सिरप या गोली उपलब्ध है?",
                "ta": "எனக்கு ஊசி பயமாக உள்ளது, சிரப் அல்லது மாத்திரை கிடைக்குமா?",
                "te": "నాకు ఇంజెక్షన్ అంటే భయం, సిరప్ లేదా మాత్ర ఉందా?",
                "kn": "ನನಗೆ ಚುಚ್ಚುಮದ್ದು ಹೆದರಿಕೆ, ಸಿರಪ್ ಅಥವಾ ಮಾತ್ರೆ ಲಭ್ಯವಿದೆಯೇ?"
            }
        ],
        "🛺 Auto-Rickshaw / Local Bus / Railway": [
            {
                "en": "Brother, please take me to the Railway Station by meter.",
                "hi": "भैया, कृपया मीटर से रेलवे स्टेशन ले चलिए।",
                "ta": "அண்ணா, தயவுசெய்து மீட்டரின்படி ரயில் நிலையத்திற்கு அழைத்துச் செல்லுங்கள்.",
                "te": "అన్నా, దయచేసి మీటర్ ప్రకారం రైల్వే స్టేషన్‌కు తీసుకెళ్లండి.",
                "kn": "ಅಣ್ಣಾ, ದಯವಿಟ್ಟು ಮೀಟರ್ ಹಾಕಿ ರೈಲ್ವೆ ನಿಲ್ದಾಣಕ್ಕೆ ಕರೆದುಕೊಂಡು ಹೋಗಿ."
            },
            {
                "en": "How much will the fare be till there?",
                "hi": "वहाँ तक का कितना किराया होगा?",
                "ta": "அங்கு செல்ல எவ்வளவு கட்டணம் ஆகும்?",
                "te": "అక్కడి వరకు ఎంత ఛార్జీ అవుతుంది?",
                "kn": "ಅಲ್ಲಿಯವರೆಗೆ ಎಷ್ಟು ಬಾಡಿಗೆ ಆಗುತ್ತದೆ?"
            },
            {
                "en": "Please alert me when the Bus Stand / Hospital stop arrives.",
                "hi": "कृपया मुझे बस स्टैंड / अस्पताल आने पर बता दीजिए।",
                "ta": "பேருந்து நிலையம் அல்லது மருத்துவமனை வரும்போது தயவுசெய்து தெரிவிக்கவும்.",
                "te": "బస్ స్టాండ్ లేదా ఆసుపత్రి వచ్చినప్పుడు దయచేసి చెప్పండి.",
                "kn": "ಬಸ್ ನಿಲ್ದಾಣ ಅಥವಾ ಆಸ್ಪತ್ರೆ ಬಂದಾಗ ದಯವಿಟ್ಟು ತಿಳಿಸಿ."
            },
            {
                "en": "I will pay via PhonePe / Google Pay / UPI QR Code.",
                "hi": "मैं फोनपे / गूगल पे / यूपीआई से भुगतान करूँगा।",
                "ta": "நான் PhonePe / Google Pay / UPI மூலம் பணம் செலுத்துவேன்.",
                "te": "నేను ఫోన్‌పే / గూగుల్ పే / UPI ద్వారా చెల్లిస్తాను.",
                "kn": "ನಾನು ಫೋನ್‌ಪೇ / ಗೂಗಲ್ ಪೇ / ಯುಪಿಐ ಮೂಲಕ ಹಣ ಪಾವತಿಸುತ್ತೇನೆ."
            }
        ],
        "🛒 Kirana / Ration / Grocery Shop": [
            {
                "en": "Please give 1 kg Arhar Dal and 500g sugar.",
                "hi": "भैया, 1 किलो अरहर दाल और आधा किलो चीनी दीजिए।",
                "ta": "ஒரு கிலோ துவரம் பருப்பு மற்றும் அரை கிலோ சர்க்கரை கொடுங்கள்.",
                "te": "ఒక కిలో కందిపప్పు మరియు అర కిలో చక్కెర ఇవ్వండి.",
                "kn": "ಒಂದು ಕೆಜಿ ತೊಗರಿ ಬೇಳೆ ಮತ್ತು ಅರ್ಧ ಕೆಜಿ ಸಕ್ಕರೆ ಕೊಡಿ."
            },
            {
                "en": "What is the total amount in Rupees?",
                "hi": "कुल कितना रुपया हुआ?",
                "ta": "மொத்தம் எத்தனை ரூபாய் ஆனது?",
                "te": "మొత్తం ఎంత రూపాయలు అయ్యింది?",
                "kn": "ಒಟ್ಟು ಎಷ್ಟು ರೂಪಾಯಿ ಆಯಿತು?"
            },
            {
                "en": "Please give me a printed or written bill receipt.",
                "hi": "कृपया मुझे पक्की रसीद या बिल दीजिए।",
                "ta": "தயவுசெய்து எனக்கு ரசீது அல்லது பில் கொடுங்கள்.",
                "te": "దయచేసి నాకు రసీదు లేదా బిల్లు ఇవ్వండి.",
                "kn": "ದಯವಿಟ್ಟು ನನಗೆ ರಶೀದಿ ಅಥವಾ ಬಿಲ್ಲು ಕೊಡಿ."
            },
            {
                "en": "Do you have change for a ₹500 note?",
                "hi": "क्या आपके पास 500 रुपये के छुट्टे हैं?",
                "ta": "உங்களிடம் 500 ரூபாய் சில்லறை உள்ளதா?",
                "te": "మీ వద్ద 500 రూపాయల చిల్లర ఉందా?",
                "kn": "ನಿಮ್ಮ ಬಳಿ 500 ರೂಪಾಯಿಯ ಚಿಲ್ಲರೆ ಇದೆಯೇ?"
            }
        ],
        "🏛️ Panchayat / Post Office / Government Center": [
            {
                "en": "I need the application form for UDID Unique Disability ID Card.",
                "hi": "मुझे यूडीआईडी (UDID) दिव्यांग पहचान पत्र का फॉर्म चाहिए।",
                "ta": "எனக்கு UDID மாற்றுத்திறனாளி அடையாள அட்டை விண்ணப்பப் படிவம் வேண்டும்.",
                "te": "నాకు UDID దివ్యాంగ గుర్తింపు కార్డు దరఖాస్తు ఫారమ్ కావాలి.",
                "kn": "ನನಗೆ ಯುಡಿಐಡಿ (UDID) ವಿಕಲಚೇತನ ಗುರುತಿನ ಚೀಟಿ ಅರ್ಜಿ ನಮೂನೆ ಬೇಕು."
            },
            {
                "en": "Which documents (Aadhaar, medical certificate) are required?",
                "hi": "इसके लिए कौन-से सरकारी दस्तावेज़ जमा करने होंगे?",
                "ta": "இதற்கு என்னென்ன ஆவணங்கள் சமர்ப்பிக்க வேண்டும்?",
                "te": "దీనికి ఏ ఏ ధ్రువీకరణ పత్రాలు సమర్పించాలి?",
                "kn": "ಇದಕ್ಕಾಗಿ ಯಾವ ದಾಖಲೆಗಳನ್ನು ಸಲ್ಲಿಸಬೇಕು?"
            },
            {
                "en": "Please assist me with filling out this form.",
                "hi": "कृपया फॉर्म भरने में मेरी सहायता कीजिए।",
                "ta": "படிவத்தை நிரப்ப தயவுசெய்து எனக்கு உதவுங்கள்.",
                "te": "ఫారమ్ నింపడంలో దయచేసి నాకు సహాయం చేయండి.",
                "kn": "ಅರ್ಜಿ ತುಂಬಲು ದಯವಿಟ್ಟು ನನಗೆ ಸಹಾಯ ಮಾಡಿ."
            }
        ]
    }

    def __init__(self):
        pass

    def get_situations(self) -> List[str]:
        return list(self.SITUATIONS.keys())

    def get_phrases(self, situation: str) -> List[Dict[str, str]]:
        return self.SITUATIONS.get(situation, self.SITUATIONS["🏥 Clinic / Hospital / Chemist"])

    def get_translated_text(self, phrase_dict: Dict[str, str], lang: str) -> str:
        lang_key = lang.lower()[:2]
        if lang_key in phrase_dict:
            return phrase_dict[lang_key]
        return phrase_dict.get("hi", phrase_dict.get("en", ""))
