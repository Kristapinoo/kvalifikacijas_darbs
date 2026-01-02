"""
Mock Claude API Client
Provides fake responses for testing without spending money
"""
import json

class MockClaudeAPIClient:
    """Mock client for testing without real API calls"""

    def __init__(self):
        """Initialize mock client"""
        self.model = "mock-claude-model"

    def generate_test(self, content, num_questions=10, difficulty="medium"):
        """
        Generate a mock test response

        Args:
            content (str): The educational content (not used in mock)
            num_questions (int): Number of questions to generate
            difficulty (str): Difficulty level

        Returns:
            dict: Mock JSON response with test structure
        """
        # Generate mock questions based on num_questions
        mock_questions = self._generate_mock_questions(num_questions, difficulty)

        return {
            "assignments": [
                {
                    "title": "1. Uzdevums - Pamata jautājumi",
                    "description": "Pārbaudi savas zināšanas par pamata jēdzieniem",
                    "max_points": 50,
                    "questions": mock_questions[:num_questions//2 + 1]
                },
                {
                    "title": "2. Uzdevums - Padziļināti jautājumi",
                    "description": "Dziļāka izpratne par tēmu",
                    "max_points": 50,
                    "questions": mock_questions[num_questions//2 + 1:num_questions]
                }
            ]
        }

    def generate_study_material(self, content):
        """
        Generate mock study material response

        Args:
            content (str): The educational content (not used in mock)

        Returns:
            dict: Mock JSON response with summary and terms
        """
        return {
            "summary": "Šis ir automātiski ģenerēts kopsavilkums par sniegto mācību materiālu. "
                      "Materiāls aptver galvenās tēmas un konceptus, kas ir svarīgi studentiem. "
                      "Kopsavilkums ietver būtiskākās idejas un palīdz labāk izprast saturu. "
                      "Tas ir strukturēts tā, lai studentiem būtu vieglāk apgūt materiālu.",
            "terms": [
                {
                    "name": "Galvenais jēdziens 1",
                    "definition": "Skaidrojums par pirmo svarīgo jēdzienu, kas palīdz izprast tēmu"
                },
                {
                    "name": "Galvenais jēdziens 2",
                    "definition": "Detalizēts skaidrojums par otro nozīmīgo terminu"
                },
                {
                    "name": "Galvenais jēdziens 3",
                    "definition": "Izskaidrojums par trešo būtisko konceptu materiālā"
                },
                {
                    "name": "Galvenais jēdziens 4",
                    "definition": "Definīcija ceturtajam svarīgam terminam"
                },
                {
                    "name": "Galvenais jēdziens 5",
                    "definition": "Paskaidrojums par piekto atslēgas jēdzienu"
                },
                {
                    "name": "Galvenais jēdziens 6",
                    "definition": "Izpratne par sesto nozīmīgo terminu"
                },
                {
                    "name": "Galvenais jēdziens 7",
                    "definition": "Apraksts septītajam fundamentālam konceptam"
                },
                {
                    "name": "Galvenais jēdziens 8",
                    "definition": "Definīcija astotajam būtiskam jēdzienam"
                },
                {
                    "name": "Galvenais jēdziens 9",
                    "definition": "Skaidrojums par devīto svarīgo terminu tēmā"
                },
                {
                    "name": "Galvenais jēdziens 10",
                    "definition": "Paskaidrojums desmitajam galvenajam konceptam"
                }
            ]
        }

    def _generate_mock_questions(self, num_questions, difficulty):
        """Generate mock questions of various types"""
        question_types = [
            "multiple_choice",
            "short_answer",
            "long_answer",
            "true_false",
            "matching",
            "fill_in_blank"
        ]

        questions = []

        for i in range(num_questions):
            q_type = question_types[i % len(question_types)]

            if q_type == "multiple_choice":
                questions.append({
                    "question_text": f"Vairāku izvēļu jautājums #{i+1}: Kura no šīm atbildēm ir pareiza?",
                    "question_type": "multiple_choice",
                    "options": ["Atbilde A", "Atbilde B", "Atbilde C", "Atbilde D"],
                    "correct_answer": "Atbilde B",
                    "points": 5
                })
            elif q_type == "short_answer":
                questions.append({
                    "question_text": f"Īsās atbildes jautājums #{i+1}: Apraksti galveno ideju.",
                    "question_type": "short_answer",
                    "options": [],
                    "correct_answer": "Īss un konkrēts atbildes paraugs",
                    "points": 10
                })
            elif q_type == "long_answer":
                questions.append({
                    "question_text": f"Garās atbildes jautājums #{i+1}: Detalizēti izskaidro procesu.",
                    "question_type": "long_answer",
                    "options": [],
                    "correct_answer": "Detalizēta atbilde ar vairākiem punktiem un paskaidrojumiem",
                    "points": 15
                })
            elif q_type == "true_false":
                questions.append({
                    "question_text": f"Patiess/Nepatiess jautājums #{i+1}: Šis apgalvojums ir patiess.",
                    "question_type": "true_false",
                    "options": ["Patiess", "Nepatiess"],
                    "correct_answer": "Patiess",
                    "points": 3
                })
            elif q_type == "matching":
                questions.append({
                    "question_text": f"Atbilžu jautājums #{i+1}: Savieno pareizos pārus.",
                    "question_type": "matching",
                    "options": ["Pāris 1A-1B", "Pāris 2A-2B", "Pāris 3A-3B"],
                    "correct_answer": "1A-1B, 2A-2B, 3A-3B",
                    "points": 8
                })
            else:  # fill_in_blank
                questions.append({
                    "question_text": f"Aizpildīšanas jautājums #{i+1}: Process notiek _____.",
                    "question_type": "fill_in_blank",
                    "options": [],
                    "correct_answer": "hloroplastu tilikoidos",
                    "points": 5
                })

        return questions


def get_mock_claude_client():
    """Get mock Claude API client instance"""
    return MockClaudeAPIClient()
