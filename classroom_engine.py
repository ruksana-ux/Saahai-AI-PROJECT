"""
Sahaaya AI — Accessible Indian Classroom & OCR Engine (Pure Python)
Worksheet text summarizer, read-aloud preparer, and automated student comprehension tester.
"""

from typing import Dict, List, Any


class SahaayaClassroomEngine:
    """
    100% Python Classroom Assistant for inclusive Indian schools.
    Integrates NCERT-aligned sample texts and automated comprehension assessments.
    """

    CURRICULUM_LESSONS = {
        "Class 5 Science: Photosynthesis (प्रकाश संश्लेषण)": {
            "text": "How Plants Make Food (प्रकाश संश्लेषण): Green plants use sunlight, water from the soil, and carbon dioxide from the air to prepare their own food. This process is called Photosynthesis. During this process, plants release oxygen into the atmosphere, which all humans and animals breathe. Chlorophyll in leaves absorbs light and gives them their green color.",
            "simplified": "Plants make food using sunlight, water, and air. This makes clean oxygen for us to breathe. Leaves are green because of chlorophyll.",
            "questions": [
                {
                    "q": "What essential gas do green plants release during photosynthesis?",
                    "options": ["Oxygen (ऑक्सीजन)", "Carbon dioxide", "Nitrogen"],
                    "correct": "Oxygen (ऑक्सीजन)",
                    "feedback": "Correct! Oxygen is released into the atmosphere, allowing humans and animals to breathe."
                },
                {
                    "q": "What gives green leaves their color?",
                    "options": ["Soil minerals", "Chlorophyll (क्लोरोफिल)", "Rainwater"],
                    "correct": "Chlorophyll (क्लोरोफिल)",
                    "feedback": "Correct! Chlorophyll absorbs sunlight and provides the vibrant green pigment."
                },
                {
                    "q": "Where do plants absorb water from?",
                    "options": ["Soil and Roots", "Clouds only", "Dry air"],
                    "correct": "Soil and Roots",
                    "feedback": "Correct! Plant roots absorb groundwater and dissolved minerals."
                }
            ],
            "related_isl_signs": ["Plant", "Sun", "Water", "Food", "Air"]
        },
        "Class 8 Civics: RPwD Act 2016 Rights & Reservations": {
            "text": "The Rights of Persons with Disabilities (RPwD) Act 2016 guarantees equal opportunity, non-discrimination, and universal design across India. It mandates 4% reservation in government jobs and 5% reservation in higher education institutions for persons with benchmark disabilities. It strictly penalizes discrimination in schools and public transit.",
            "simplified": "The RPwD Act 2016 gives 4% job quota and 5% college quota for persons with disabilities. It orders all public buildings to build ramps and accessible toilets.",
            "questions": [
                {
                    "q": "What percent reservation in government jobs is mandated under RPwD Act 2016?",
                    "options": ["2%", "4%", "10%"],
                    "correct": "4%",
                    "feedback": "Correct! The Act guarantees 4% job reservations in central and state government departments."
                },
                {
                    "q": "What reservation percentage is provided in government higher education?",
                    "options": ["5%", "1%", "8%"],
                    "correct": "5%",
                    "feedback": "Correct! 5% seats are reserved in higher education institutions."
                },
                {
                    "q": "What does the Act mandate for public railway stations and buildings?",
                    "options": ["Accessible ramps and lifts", "Stairs only", "No changes"],
                    "correct": "Accessible ramps and lifts",
                    "feedback": "Correct! Mandatory retrofitting with universal ramps, tactile tiles, and accessible restrooms."
                }
            ],
            "related_isl_signs": ["School", "Law / Rights", "Help", "Equal", "Study"]
        },
        "Class 4 Math: Everyday Kirana Bill & Calculation": {
            "text": "Everyday Kirana Bill: Rahul bought 1 kg rice for ₹50, 1 packet milk for ₹28, and soap for ₹22. Total amount = 50 + 28 + 22 = ₹100. Rahul handed a ₹200 note to the shopkeeper. Change to receive back = 200 - 100 = ₹100.",
            "simplified": "Items cost ₹50 + ₹28 + ₹22 = ₹100. Giving a ₹200 note means the shopkeeper must return ₹100 as change.",
            "questions": [
                {
                    "q": "What was the total cost of all the purchased groceries?",
                    "options": ["₹100", "₹80", "₹120"],
                    "correct": "₹100",
                    "feedback": "Correct! 50 + 28 + 22 equals exactly ₹100."
                },
                {
                    "q": "Which banknote did Rahul hand to the shopkeeper?",
                    "options": ["₹500 note", "₹200 note", "₹50 note"],
                    "correct": "₹200 note",
                    "feedback": "Correct! Rahul handed over a bright yellow ₹200 note."
                },
                {
                    "q": "How much change should the shopkeeper return to Rahul?",
                    "options": ["₹100", "₹50", "₹20"],
                    "correct": "₹100",
                    "feedback": "Correct! 200 minus 100 leaves ₹100 in change."
                }
            ],
            "related_isl_signs": ["Money / Rupee", "Buy", "Number", "Yes", "Thank You"]
        }
    }

    def __init__(self):
        pass

    def get_lesson_titles(self) -> List[str]:
        return list(self.CURRICULUM_LESSONS.keys())

    def get_lesson(self, title: str) -> Dict[str, Any]:
        return self.CURRICULUM_LESSONS.get(title, self.CURRICULUM_LESSONS["Class 5 Science: Photosynthesis (प्रकाश संश्लेषण)"])
