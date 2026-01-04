"""
Claude API Client
Handles communication with Claude AI for generating tests and study materials
"""
import os
import json
from anthropic import Anthropic, APIError
from dotenv import load_dotenv

load_dotenv()

class ClaudeAPIClient:
    """Client for interacting with Claude API"""

    def __init__(self):
        """Initialize Claude API client"""
        self.api_key = os.getenv('CLAUDE_API_KEY')
        if not self.api_key:
            raise ValueError("CLAUDE_API_KEY not found in environment variables")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5 (latest stable)

    def generate_test(self, content, num_questions=10, difficulty="medium"):
        """
        Generate a test from content using Claude AI

        Args:
            content (str): The educational content to create a test from
            num_questions (int): Number of questions to generate (default: 10)
            difficulty (str): Difficulty level - "easy", "medium", or "hard" (default: "medium")

        Returns:
            dict: JSON response with test structure (assignments with questions)

        Raises:
            APIError: If Claude API request fails
            ValueError: If response cannot be parsed
        """
        prompt = self._build_test_prompt(content, num_questions, difficulty)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            response_text = response.content[0].text

            # Parse JSON from response
            test_data = self._extract_json(response_text)

            return test_data

        except APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to generate test: {str(e)}")

    def generate_study_material(self, content):
        """
        Generate a study material (summary + terms) from content using Claude AI

        Args:
            content (str): The educational content to create study material from

        Returns:
            dict: JSON response with summary and terms

        Raises:
            APIError: If Claude API request fails
            ValueError: If response cannot be parsed
        """
        prompt = self._build_study_material_prompt(content)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            response_text = response.content[0].text

            # Parse JSON from response
            material_data = self._extract_json(response_text)

            return material_data

        except APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to generate study material: {str(e)}")

    def generate_additional_questions(self, context, num_questions=3, difficulty="medium"):
        """
        Generate additional questions for an existing assignment using Claude AI

        Args:
            context (str): The assignment title and description for context
            num_questions (int): Number of questions to generate (default: 3)
            difficulty (str): Difficulty level - "easy", "medium", or "hard" (default: "medium")

        Returns:
            dict: JSON response with assignment containing questions

        Raises:
            APIError: If Claude API request fails
            ValueError: If response cannot be parsed
        """
        prompt = self._build_additional_questions_prompt(context, num_questions, difficulty)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text from response
            response_text = response.content[0].text

            # Parse JSON from response
            questions_data = self._extract_json(response_text)

            return questions_data

        except APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to generate additional questions: {str(e)}")

    def _build_test_prompt(self, content, num_questions, difficulty):
        """Build prompt for test generation"""

        difficulty_instructions = {
            "easy": "Izveido vienkāršus, tiešus jautājumus, kas pārbauda pamata izpratni.",
            "medium": "Izveido vidēji grūtus jautājumus, kas pārbauda izpratni un pielietojumu.",
            "hard": "Izveido grūtus jautājumus, kas pārbauda dziļu izpratni, analīzi un kritisko domāšanu."
        }

        difficulty_text = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])

        prompt = f"""Tu esi eksperts mācību satura veidošanā. Pamatojoties uz šo mācību saturu, izveido testu ar PRECĪZI {num_questions} jautājumiem.

{difficulty_text}

SVARĪGI: Viss saturs (uzdevumu nosaukumi, apraksti, jautājumi, atbildes) jāģenerē LATVIEŠU VALODĀ!

MĀCĪBU SATURS:
{content}

PRASĪBAS:
1. Izveido PRECĪZI {num_questions} jautājumus KOPĀ (ne vairāk, ne mazāk)
2. Ja izveidoji vairākus uzdevumus (assignments), tad VISU uzdevumu jautājumu SUMMAI jābūt TIEŠI {num_questions}
3. Izmanto dažādus jautājumu tipus ar atbilstošām punktu vērtībām:
   - multiple_choice (ar 4 atbilžu variantiem A, B, C, D) - 1-3 punkti
   - true_false (patiess vai nepatiess) - 1-2 punkti
   - fill_in_blank (teksts ar tukšumiem aizpildīšanai) - 1-3 punkti
   - matching (pāri saskaņošanai) - 2-5 punkti
   - short_answer (īsa teksta atbilde) - 3-5 punkti
   - long_answer (detalizēta esejas atbilde) - 5-10 punkti
4. Organizē jautājumus loģiskos uzdevumos/sadaļās
5. Katram jautājumam jābūt:
   - Skaidram jautājuma tekstam
   - Jautājuma tipam
   - Pareizajai atbildei
   - Punktu vērtībai (atbilstoši jautājuma tipam - skat. augstāk)
   - Jautājumiem ar multiple_choice: nodrošini 4 atbilžu variantus
6. Multiple choice jautājumiem:
   - Variē pareizās atbildes pozīciju katrā jautājumā
   - Izvairīties no vienas pozīcijas dominances (piemēram, ne visas B)
   - Pareizā atbilde var būt A, B, C vai D jebkurā jautājumā
   - Izvieto pareizās atbildes nejauši un vienmērīgi

IZVADES FORMĀTS:
Atgriez TIKAI derīgu JSON objektu (bez markdown, bez paskaidrojumiem) ar šādu precīzu struktūru:

{{
  "assignments": [
    {{
      "title": "Uzdevuma nosaukums",
      "description": "Īss šīs sadaļas apraksts",
      "max_points": 25,
      "questions": [
        {{
          "question_text": "Pirmais jautājums?",
          "question_type": "multiple_choice",
          "options": ["Variants A", "Variants B", "Variants C", "Variants D"],
          "correct_answer": "Variants A",
          "points": 2
        }},
        {{
          "question_text": "Otrais jautājums?",
          "question_type": "multiple_choice",
          "options": ["Variants A", "Variants B", "Variants C", "Variants D"],
          "correct_answer": "Variants D",
          "points": 2
        }},
        {{
          "question_text": "Patiess vai nepatiess jautājums?",
          "question_type": "true_false",
          "options": ["Patiess", "Nepatiess"],
          "correct_answer": "Patiess",
          "points": 1
        }},
        {{
          "question_text": "Trešais jautājums?",
          "question_type": "multiple_choice",
          "options": ["Variants A", "Variants B", "Variants C", "Variants D"],
          "correct_answer": "Variants B",
          "points": 2
        }},
        {{
          "question_text": "Īsās atbildes jautājums?",
          "question_type": "short_answer",
          "options": [],
          "correct_answer": "Paredzamā atbilde",
          "points": 4
        }},
        {{
          "question_text": "Detalizētas atbildes jautājums?",
          "question_type": "long_answer",
          "options": [],
          "correct_answer": "Detalizēta atbilde ar vairākām rindkopām",
          "points": 8
        }}
      ]
    }}
  ]
}}

SVARĪGI:
- Atgriez TIKAI JSON objektu, neko citu
- Viss teksts (nosaukumi, apraksti, jautājumi, atbildes) jāraksta LATVIEŠU VALODĀ
- ĻOTI SVARĪGI: Jāizveido PRECĪZI {num_questions} jautājumi kopā visos uzdevumos
- Ja pieprasīti 4 jautājumi, tad kopā drīkst būt TIKAI 4 jautājumi, ne 5, ne 10, ne 15
- Pārliecinies, ka viss JSON ir pareizi formatēts
- Izmanto dubultpēdiņas virknēm
- Iekļauj visus nepieciešamos laukus"""

        return prompt

    def _build_study_material_prompt(self, content):
        """Build prompt for study material generation"""

        prompt = f"""Tu esi eksperts mācību satura veidošanā. Pamatojoties uz šo mācību saturu, izveido visaptverošu mācību materiālu.

SVARĪGI: Viss saturs (kopsavilkums, termini, definīcijas) jāģenerē LATVIEŠU VALODĀ!

MĀCĪBU SATURS:
{content}

PRASĪBAS:
1. Izveido skaidru, kodolīgu galveno jēdzienu kopsavilkumu (2-4 rindkopas)
2. Izvelc un definē 10-15 galvenos terminus/jēdzienus no satura
3. Katram terminam jābūt skaidrai, studentiem draudzīgai definīcijai
4. Koncentrējies uz svarīgākajiem jēdzieniem mācībām

IZVADES FORMĀTS:
Atgriez TIKAI derīgu JSON objektu (bez markdown, bez paskaidrojumiem) ar šādu precīzu struktūru:

{{
  "summary": "Visaptverošs satura kopsavilkums, kas aptver galvenās idejas, galvenos jēdzienus un svarīgus punktus. Šim jābūt 2-4 rindkopām, kas sniedz studentiem labu pārskatu par tēmu.",
  "terms": [
    {{
      "name": "Galvenais termins 1",
      "definition": "Skaidra definīcija, kas nozīmē šis termins satura kontekstā"
    }},
    {{
      "name": "Galvenais termins 2",
      "definition": "Skaidra definīcija, kas nozīmē šis termins satura kontekstā"
    }}
  ]
}}

SVARĪGI:
- Atgriez TIKAI JSON objektu, neko citu
- Pārliecinies, ka viss JSON ir pareizi formatēts
- Izmanto dubultpēdiņas virknēm
- Kopsavilkumam jābūt informatīvam un visaptverošam
- Definīcijām jābūt skaidrām un izglītojošām
- Saturs jāraksta LATVIEŠU VALODĀ"""

        return prompt

    def _build_additional_questions_prompt(self, context, num_questions, difficulty):
        """Build prompt for generating additional questions for an existing assignment"""

        difficulty_instructions = {
            "easy": "Izveido vienkāršus, tiešus jautājumus, kas pārbauda pamata izpratni.",
            "medium": "Izveido vidēji grūtus jautājumus, kas pārbauda izpratni un pielietojumu.",
            "hard": "Izveido grūtus jautājumus, kas pārbauda dziļu izpratni, analīzi un kritisko domāšanu."
        }

        difficulty_text = difficulty_instructions.get(difficulty, difficulty_instructions["medium"])

        prompt = f"""Tu esi eksperts mācību satura veidošanā. Pamatojoties uz šo uzdevuma kontekstu, izveido {num_questions} papildu jautājumus.

{difficulty_text}

SVARĪGI: Visi jautājumi un atbildes jāģenerē LATVIEŠU VALODĀ!

UZDEVUMA KONTEKSTS:
{context}

PRASĪBAS:
1. Izveido {num_questions} jaunus jautājumus
2. Izmanto dažādus jautājumu tipus:
   - multiple_choice (ar 4 atbilžu variantiem A, B, C, D)
   - short_answer (īsa teksta atbilde)
   - long_answer (detalizēta esejas atbilde)
   - true_false (patiess vai nepatiess)
   - matching (pāri saskaņošanai)
   - fill_in_blank (teksts ar tukšumiem aizpildīšanai)
3. Katram jautājumam jābūt:
   - Skaidram jautājuma tekstam
   - Jautājuma tipam
   - Pareizajai atbildei
   - Punktu vērtībai (1-10 punkti atkarībā no grūtības pakāpes)
   - Jautājumiem ar multiple_choice: nodrošini 4 atbilžu variantus
4. Jautājumiem jāattiecas uz sniegto uzdevuma kontekstu

IZVADES FORMĀTS:
Atgriez TIKAI derīgu JSON objektu (bez markdown, bez paskaidrojumiem) ar šādu precīzu struktūru:

{{
  "assignments": [
    {{
      "title": "Jautājumi",
      "description": "Papildu jautājumi",
      "max_points": 0,
      "questions": [
        {{
          "question_text": "Jautājuma teksts?",
          "question_type": "multiple_choice",
          "options": ["Variants A", "Variants B", "Variants C", "Variants D"],
          "correct_answer": "Variants B",
          "points": 5
        }},
        {{
          "question_text": "Patiess vai nepatiess jautājums?",
          "question_type": "true_false",
          "options": ["Patiess", "Nepatiess"],
          "correct_answer": "Patiess",
          "points": 2
        }},
        {{
          "question_text": "Īsās atbildes jautājums?",
          "question_type": "short_answer",
          "options": [],
          "correct_answer": "Paredzamā atbilde",
          "points": 5
        }}
      ]
    }}
  ]
}}

SVARĪGI:
- Atgriez TIKAI JSON objektu, neko citu
- Pārliecinies, ka viss JSON ir pareizi formatēts
- Izmanto dubultpēdiņas virknēm
- Iekļauj visus nepieciešamos laukus
- Izveido augstas kvalitātes, atbilstošus jautājumus
- Viss teksts jāraksta LATVIEŠU VALODĀ"""

        return prompt

    def _extract_json(self, text):
        """
        Extract and parse JSON from Claude's response

        Args:
            text (str): Response text from Claude

        Returns:
            dict: Parsed JSON object

        Raises:
            ValueError: If JSON cannot be extracted or parsed
        """
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            # Try to find JSON object in the text
            start = text.find('{')
            end = text.rfind('}') + 1

            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass

            raise ValueError(f"Could not parse JSON from response: {str(e)}")

# Singleton instance
_client = None

def get_claude_client():
    """Get or create Claude API client singleton"""
    global _client
    if _client is None:
        _client = ClaudeAPIClient()
    return _client
