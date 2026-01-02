"""
MODUĻA 2: Ģenerēšanas testi
6 testi materiālu ģenerēšanai ar Claude API
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from models import Test, StudyMaterial
import json


def test_01_generate_test_with_text(auth_client, test_db, mocker):
    """
    Nr: 1
    Testējamā funkcionalitāte: Testa ģenerēšana ar teksta saturu
    Sagaidamais rezultāts: Tests tiek izveidots ar uzdevumiem un jautājumiem
    """
    # SETUP - mock Claude API
    test_data = {
        "assignments": [{
            "title": "1. uzdevums",
            "description": "Apraksts",
            "max_points": 10,
            "questions": [{
                "question_text": "Kas ir Python?",
                "question_type": "multiple_choice",
                "correct_answer": "A",
                "points": 5,
                "options": [
                    {"option_text": "Programmēšanas valoda", "is_correct": True},
                    {"option_text": "Čūska", "is_correct": False}
                ]
            }]
        }]
    }

    mock_client = Mock()
    mock_client.generate_test = Mock(return_value=test_data)
    mocker.patch('routes.generate.get_claude_client', return_value=mock_client)

    # ACTION - ģenerē testu
    response = auth_client.post('/api/generate', data={
        'material_type': 'test',
        'title': 'Python tests',
        'content': 'Python ir programmēšanas valoda. ' * 100,
        'num_questions': 5,
        'difficulty': 'medium'
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 201, "Statuss būtu jābūt 201"
    assert 'id' in response.json, "Atbildē jābūt 'id'"

    # DB CHECK - pārbauda datu bāzi
    test = Test.query.get(response.json['id'])
    assert test is not None, "Testam būtu jābūt DB"
    assert test.title == 'Python tests', "Nosaukumam jāsakrīt"
    assert len(test.assignments) > 0, "Testam jābūt uzdevumiem"


def test_02_generate_study_material(auth_client, test_db, mocker):
    """
    Nr: 2
    Testējamā funkcionalitāte: Mācību materiāla ģenerēšana
    Sagaidamais rezultāts: Mācību materiāls tiek izveidots ar kopsavilkumu un terminiem
    """
    # SETUP - mock Claude API
    study_data = {
        "summary": "<p>Kopsavilkums par Python</p>",
        "terms": [
            {"name": "Python", "definition": "Programmēšanas valoda"}
        ]
    }

    mock_client = Mock()
    mock_client.generate_study_material = Mock(return_value=study_data)
    mocker.patch('routes.generate.get_claude_client', return_value=mock_client)

    # ACTION - ģenerē mācību materiālu
    response = auth_client.post('/api/generate', data={
        'material_type': 'study_material',
        'title': 'Python pamati',
        'content': 'Python ir programmēšanas valoda. ' * 100
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 201, "Statuss būtu jābūt 201"
    assert 'id' in response.json, "Atbildē jābūt 'id'"

    # DB CHECK - pārbauda datu bāzi
    material = StudyMaterial.query.get(response.json['id'])
    assert material is not None, "Materiālam būtu jābūt DB"
    assert material.title == 'Python pamati', "Nosaukumam jāsakrīt"
    assert 'summary' in material.content, "Saturā jābūt kopsavilkumam"


def test_03_generate_without_title(auth_client, test_db):
    """
    Nr: 3
    Testējamā funkcionalitāte: Ģenerēšana bez nosaukuma
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "title is required"
    """
    # ACTION - mēģina ģenerēt bez nosaukuma
    response = auth_client.post('/api/generate', data={
        'material_type': 'test',
        'content': 'Saturs'
    })

    # ASSERT - pārbauda kļūdu
    assert response.status_code == 400, "Statuss būtu jābūt 400"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    assert 'title' in response.json['error'].lower(), "Kļūdas ziņojumā jābūt 'title'"


def test_04_generate_short_content(auth_client, test_db):
    """
    Nr: 4
    Testējamā funkcionalitāte: Ģenerēšana ar pārāk īsu saturu
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "Content cannot be empty"
    """
    # ACTION - mēģina ģenerēt ar tukšu saturu
    response = auth_client.post('/api/generate', data={
        'material_type': 'test',
        'title': 'Tests',
        'content': '   '  # Tikai atstarpes
    })

    # ASSERT - pārbauda kļūdu
    assert response.status_code == 400, "Statuss būtu jābūt 400"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    assert 'content' in response.json['error'].lower() or 'empty' in response.json['error'].lower(), \
        "Kļūdas ziņojumā jābūt informācijai par saturu"


def test_05_claude_api_request(auth_client, test_db, mocker):
    """
    Nr: 5
    Testējamā funkcionalitāte: Claude API pieprasījums ar pareiziem parametriem
    Sagaidamais rezultāts: API tiek izsaukts ar korektiem parametriem (content, num_questions, difficulty)
    """
    # SETUP - mock Claude API client
    mock_client = Mock()
    mock_client.generate_test = Mock(return_value={
        "assignments": [{
            "title": "Uzdevums",
            "description": "Apraksts",
            "max_points": 5,
            "questions": [{
                "question_text": "Jautājums?",
                "question_type": "short_answer",
                "correct_answer": "Atbilde",
                "points": 5,
                "options": []
            }]
        }]
    })

    mocker.patch('routes.generate.get_claude_client', return_value=mock_client)

    # ACTION - ģenerē materiālu
    response = auth_client.post('/api/generate', data={
        'material_type': 'test',
        'title': 'API tests',
        'content': 'Saturs par tēmu. ' * 100,
        'num_questions': 3,
        'difficulty': 'easy'
    })

    # ASSERT - pārbauda ka API tika izsaukts
    assert mock_client.generate_test.called, "Claude API generate_test būtu jābūt izsauktam"
    call_args = mock_client.generate_test.call_args

    # Pārbauda parametrus
    assert call_args is not None, "API izsaukuma parametriem jābūt"
    assert 'content' in call_args.kwargs or len(call_args.args) > 0, "Parametros jābūt content"
    assert 'num_questions' in call_args.kwargs or len(call_args.args) > 1, "Parametros jābūt num_questions"
    assert 'difficulty' in call_args.kwargs or len(call_args.args) > 2, "Parametros jābūt difficulty"


def test_06_parse_claude_response(auth_client, test_db, mocker):
    """
    Nr: 6
    Testējamā funkcionalitāte: Claude atbildes parsēšana un validācija
    Sagaidamais rezultāts: JSON atbilde tiek pareizi parsēta un saglabāta datu bāzē
    """
    # SETUP - mock Claude API client ar derīgu atbildi
    test_data = {
        "assignments": [{
            "title": "Matemātika",
            "description": "Matemātikas uzdevumi",
            "max_points": 15,
            "questions": [
                {
                    "question_text": "Cik ir 2+2?",
                    "question_type": "multiple_choice",
                    "correct_answer": "B",
                    "points": 5,
                    "options": [
                        {"option_text": "3", "is_correct": False},
                        {"option_text": "4", "is_correct": True},
                        {"option_text": "5", "is_correct": False}
                    ]
                },
                {
                    "question_text": "Nosaki x: x + 5 = 10",
                    "question_type": "short_answer",
                    "correct_answer": "5",
                    "points": 10,
                    "options": []
                }
            ]
        }]
    }

    mock_client = Mock()
    mock_client.generate_test = Mock(return_value=test_data)
    mocker.patch('routes.generate.get_claude_client', return_value=mock_client)

    # ACTION - ģenerē testu
    response = auth_client.post('/api/generate', data={
        'material_type': 'test',
        'title': 'Matemātikas tests',
        'content': 'Matemātika ir zinātne par skaitļiem. ' * 100
    })

    # ASSERT - pārbauda parsēšanu
    if response.status_code != 201:
        print(f"ERROR: {response.json}")
    assert response.status_code == 201, f"Statuss būtu jābūt 201, bet ir {response.status_code}: {response.json if response.json else 'no json'}"

    # DB CHECK - pārbauda ka dati pareizi saglabāti
    test = Test.query.get(response.json['id'])
    assert test is not None, "Testam būtu jābūt DB"
    assert len(test.assignments) == 1, "Testam jābūt 1 uzdevumam"

    assignment = test.assignments[0]
    assert assignment.title == "Matemātika", "Uzdevuma nosaukumam jāsakrīt"
    assert len(assignment.questions) == 2, "Uzdevumam jābūt 2 jautājumiem"

    # Pārbauda pirmā jautājuma datus
    q1 = assignment.questions[0]
    assert q1.question_text == "Cik ir 2+2?", "Jautājuma tekstam jāsakrīt"
    assert q1.question_type.value == "multiple_choice", "Jautājuma tipam jāsakrīt"
    assert len(q1.options) == 3, "Jautājumam jābūt 3 opcijām"

    # Pārbauda otrā jautājuma datus
    q2 = assignment.questions[1]
    assert q2.question_type.value == "short_answer", "Jautājuma tipam jābūt short_answer"
    assert q2.correct_answer == "5", "Pareizajai atbildei jāsakrīt"
