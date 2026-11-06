"""
Sahaaya AI — Indian Sign Language (ISL) Engine (Pure Python)
ISLRTC & NCERT Channel 31 aligned dictionary, step-by-step gesture instructions,
and interactive sign quiz generator.
"""

import random
from typing import Dict, List, Any


class SahaayaISLEngine:
    """
    100% Python Engine for Indian Sign Language (ISL) Education & Practice.
    Aligned with ISLRTC (Indian Sign Language Research and Training Centre) standards.
    """

    ISL_DATA = {
        "Daily Greetings & Essentials": [
            {
                "id": "namaste",
                "name": "Namaste (नमस्ते)",
                "icon": "🙏",
                "instructions": "Both palms pressed flat together vertically in front of the chest with a respectful slight head nod.",
                "importance": "Traditional respectful Indian greeting used in schools, offices, and homes."
            },
            {
                "id": "thankyou",
                "name": "Thank You (धन्यवाद / शुक्रिया)",
                "icon": "💐",
                "instructions": "Fingertips of the right flat palm touch the lower lip/chin and move smoothly forward and outward towards the other person.",
                "importance": "Core courtesy expression in everyday communication."
            },
            {
                "id": "water",
                "name": "Water (पानी / தண்ணீர்)",
                "icon": "💧",
                "instructions": "Form a 'W' shape with index, middle, and ring fingers near the chin, or cup right hand tilting upwards toward the mouth mimicking drinking.",
                "importance": "Essential daily life sign."
            },
            {
                "id": "food",
                "name": "Food / Eat (खाना / ಊಟ)",
                "icon": "🍚",
                "instructions": "Fingertips of right hand bunched together, tapping the lips twice in a gentle eating gesture.",
                "importance": "Primary sustenance and mealtime sign."
            },
            {
                "id": "yes",
                "name": "Yes (हाँ / ஆம்)",
                "icon": "👍",
                "instructions": "Form a closed right fist at chest level, nodding the wrist up and down twice like a head nod.",
                "importance": "Universal affirmative response."
            },
            {
                "id": "no",
                "name": "No (नहीं / இல்லை)",
                "icon": "👎",
                "instructions": "Index and middle fingers extended horizontally, snapping closed against the thumb twice, or side-to-side palm shake.",
                "importance": "Universal negative response."
            }
        ],
        "Emergency & Medical Signs": [
            {
                "id": "help",
                "name": "Help / Assist (सहायता / मदद)",
                "icon": "🆘",
                "instructions": "Left hand open with palm facing upward. Right hand forms a closed fist with thumb up, placed on the left palm, both hands lifting upward together.",
                "importance": "Critical emergency assistance gesture."
            },
            {
                "id": "doctor",
                "name": "Doctor (डॉक्टर)",
                "icon": "🩺",
                "instructions": "Right index and middle fingertips tap the inner pulse point of the left wrist twice (mimicking taking a radial pulse).",
                "importance": "Hospital and clinic triage communication."
            },
            {
                "id": "medicine",
                "name": "Medicine (दवा / மருந்து)",
                "icon": "💊",
                "instructions": "Right middle fingertip rotates in the center of the flat open left palm, mimicking grinding a medicinal tablet on a stone.",
                "importance": "Pharmacy and first aid interaction."
            },
            {
                "id": "danger",
                "name": "Danger / Stop (खतरा / रुको)",
                "icon": "🛑",
                "instructions": "Right hand open with palm facing forward, thrust firmly forward in an abrupt halting motion with an alert facial expression.",
                "importance": "Immediate hazard avoidance."
            }
        ],
        "School & Learning Signs": [
            {
                "id": "school",
                "name": "School (विद्यालय / ಶಾಲೆ)",
                "icon": "🏫",
                "instructions": "Right flat palm claps gently onto the horizontal left flat palm twice in front of the chest.",
                "importance": "Inclusive classroom identification."
            },
            {
                "id": "teacher",
                "name": "Teacher (अध्यापक / ஆசிரியர்)",
                "icon": "👨‍🏫",
                "instructions": "Both hands pinch index and thumb at temples, moving forward and opening downwards into flat palms.",
                "importance": "Respectful educator address."
            },
            {
                "id": "book",
                "name": "Book / Read (किताब / புத்தகம்)",
                "icon": "📖",
                "instructions": "Both palms pressed flat together vertically, then opened outward like turning the covers of a textbook.",
                "importance": "Classroom study and homework."
            },
            {
                "id": "write",
                "name": "Write (लिखना / எழுது)",
                "icon": "✍️",
                "instructions": "Right thumb and index pinch as if holding a pen, moving horizontally across the open flat left palm.",
                "importance": "Exam and note-taking interaction."
            }
        ],
        "Numbers 1-10": [
            {
                "id": "num1",
                "name": "Number 1 (एक)",
                "icon": "☝️",
                "instructions": "Right index finger pointed vertically upward with back of hand facing the viewer.",
                "importance": "Counting and ordering."
            },
            {
                "id": "num2",
                "name": "Number 2 (दो)",
                "icon": "✌️",
                "instructions": "Right index and middle finger extended upward in a clear V-shape.",
                "importance": "Counting and price calculation."
            },
            {
                "id": "num5",
                "name": "Number 5 (पाँच)",
                "icon": "🖐️",
                "instructions": "Open right hand with all 5 fingers spread and extended facing forward.",
                "importance": "Counting and denomination exchange."
            },
            {
                "id": "num10",
                "name": "Number 10 (दस)",
                "icon": "👐",
                "instructions": "Both hands held up with all 10 fingers extended, or shaking right thumb vigorously upward.",
                "importance": "Curricular math and shopping."
            }
        ]
    }

    def __init__(self):
        pass

    def get_categories(self) -> List[str]:
        return list(self.ISL_DATA.keys())

    def get_signs_by_category(self, cat: str) -> List[Dict[str, Any]]:
        return self.ISL_DATA.get(cat, self.ISL_DATA["Daily Greetings & Essentials"])

    def generate_quiz_question(self) -> Dict[str, Any]:
        """Generates a randomized multiple-choice ISL sign quiz question."""
        all_signs = []
        for signs in self.ISL_DATA.values():
            all_signs.extend(signs)

        target = random.choice(all_signs)
        distractors = [s for s in all_signs if s["id"] != target["id"]]
        random.shuffle(distractors)
        options = [target] + distractors[:2]
        random.shuffle(options)

        return {
            "target": target,
            "question": f"Which gesture corresponds to: '{target['name']}'?",
            "options": options,
            "correct_id": target["id"],
            "explanation": f"✅ {target['name']}: {target['instructions']}"
        }
