"""
MODUĻA 3: Rediģēšanas testi
6 testi materiālu rediģēšanai un modificēšanai
"""
import pytest
from models import Test, Question


def test_01_edit_question_text(auth_client, test_test_material, app):
    """
    Nr: 1
    Testējamā funkcionalitāte: Jautājuma teksta rediģēšana
    Sagaidamais rezultāts: Jautājuma teksts tiek veiksmīgi atjaunināts datu bāzē
    """
    # SETUP - iegūst esošo testu
    with app.app_context():
        test = Test.query.get(test_test_material['test_id'])
        original_question_text = test.assignments[0].questions[0].question_text

    # ACTION - rediģē jautājuma tekstu
    response = auth_client.put(f'/api/materials/{test_test_material["test_id"]}', json={
        'type': 'test',
        'title': 'Atjaunināts tests',
        'assignments': [{
            'id': test_test_material['assignment_id'],
            'title': '1. uzdevums',
            'description': 'Uzdevuma apraksts',
            'max_points': 10,
            'questions': [{
                'id': test_test_material['question_id'],
                'question_text': 'Jauns jautājuma teksts?',
                'question_type': 'multiple_choice',
                'correct_answer': 'A',
                'points': 5,
                'options': []
            }]
        }]
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda datu bāzi
    with app.app_context():
        question = Question.query.get(test_test_material['question_id'])
        assert question is not None, "Jautājumam būtu jābūt DB"
        assert question.question_text == 'Jauns jautājuma teksts?', "Jautājuma tekstam jābūt atjauninātam"
        assert question.question_text != original_question_text, "Tekstam jāatšķiras no oriģinālā"


def test_02_change_question_type(auth_client, test_test_material, app):
    """
    Nr: 2
    Testējamā funkcionalitāte: Jautājuma tipa maiņa (no multiple_choice uz short_answer)
    Sagaidamais rezultāts: Jautājuma tips tiek veiksmīgi nomainīts
    """
    # ACTION - maina jautājuma tipu
    response = auth_client.put(f'/api/materials/{test_test_material["test_id"]}', json={
        'type': 'test',
        'title': 'Tests',
        'assignments': [{
            'id': test_test_material['assignment_id'],
            'title': '1. uzdevums',
            'description': 'Apraksts',
            'max_points': 10,
            'questions': [{
                'id': test_test_material['question_id'],
                'question_text': 'Kas ir Python?',
                'question_type': 'short_answer',  # Mainīts no multiple_choice
                'correct_answer': 'Programmēšanas valoda',
                'points': 5,
                'options': []
            }]
        }]
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda datu bāzi
    with app.app_context():
        question = Question.query.get(test_test_material['question_id'])
        assert question is not None, "Jautājumam būtu jābūt DB"
        assert question.question_type.value == 'short_answer', "Jautājuma tipam jābūt short_answer"


def test_03_edit_answer(auth_client, test_test_material, app):
    """
    Nr: 3
    Testējamā funkcionalitāte: Pareizās atbildes rediģēšana
    Sagaidamais rezultāts: Pareizā atbilde tiek veiksmīgi atjaunināta
    """
    # ACTION - rediģē pareizo atbildi
    response = auth_client.put(f'/api/materials/{test_test_material["test_id"]}', json={
        'type': 'test',
        'title': 'Tests',
        'assignments': [{
            'id': test_test_material['assignment_id'],
            'title': '1. uzdevums',
            'description': 'Apraksts',
            'max_points': 10,
            'questions': [{
                'id': test_test_material['question_id'],
                'question_text': 'Kas ir Python?',
                'question_type': 'short_answer',
                'correct_answer': 'Jauna pareizā atbilde',  # Mainīta atbilde
                'points': 5,
                'options': []
            }]
        }]
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda datu bāzi
    with app.app_context():
        question = Question.query.get(test_test_material['question_id'])
        assert question is not None, "Jautājumam būtu jābūt DB"
        assert question.correct_answer == 'Jauna pareizā atbilde', "Pareizajai atbildei jābūt atjauninātai"


def test_04_change_points(auth_client, test_test_material, app):
    """
    Nr: 4
    Testējamā funkcionalitāte: Jautājuma punktu skaita maiņa
    Sagaidamais rezultāts: Punktu skaits tiek veiksmīgi atjaunināts
    """
    # ACTION - maina punktu skaitu
    response = auth_client.put(f'/api/materials/{test_test_material["test_id"]}', json={
        'type': 'test',
        'title': 'Tests',
        'assignments': [{
            'id': test_test_material['assignment_id'],
            'title': '1. uzdevums',
            'description': 'Apraksts',
            'max_points': 15,  # Atjaunināts
            'questions': [{
                'id': test_test_material['question_id'],
                'question_text': 'Kas ir Python?',
                'question_type': 'short_answer',
                'correct_answer': 'Atbilde',
                'points': 15,  # Mainīts no 5 uz 15
                'options': []
            }]
        }]
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda datu bāzi
    with app.app_context():
        question = Question.query.get(test_test_material['question_id'])
        assert question is not None, "Jautājumam būtu jābūt DB"
        assert question.points == 15, "Punktiem jābūt 15"


def test_05_delete_question(auth_client, test_test_material, app):
    """
    Nr: 5
    Testējamā funkcionalitāte: Jautājuma dzēšana no testa
    Sagaidamais rezultāts: Jautājums tiek veiksmīgi izdzēsts no uzdevuma
    """
    # ACTION - dzēš jautājumu (neiekļaujot to atjauninātajā sarakstā)
    response = auth_client.put(f'/api/materials/{test_test_material["test_id"]}', json={
        'type': 'test',
        'title': 'Tests',
        'assignments': [{
            'id': test_test_material['assignment_id'],
            'title': '1. uzdevums',
            'description': 'Apraksts',
            'max_points': 0,
            'questions': []  # Tukšs jautājumu saraksts = visi dzēsti
        }]
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda ka jautājums ir dzēsts
    with app.app_context():
        test = Test.query.get(test_test_material['test_id'])
        assert test is not None, "Testam būtu jābūt DB"
        assert len(test.assignments[0].questions) == 0, "Uzdevumam nevajadzētu būt jautājumiem"


def test_06_add_question(auth_client, test_test_material, app):
    """
    Nr: 6
    Testējamā funkcionalitāte: Jauna jautājuma pievienošana esošam uzdevumam
    Sagaidamais rezultāts: Jaunais jautājums tiek veiksmīgi pievienots
    """
    # SETUP - iegūst esošo jautājumu skaitu
    with app.app_context():
        test = Test.query.get(test_test_material['test_id'])
        original_count = len(test.assignments[0].questions)

    # ACTION - pievieno jaunu jautājumu
    response = auth_client.put(f'/api/materials/{test_test_material["test_id"]}', json={
        'type': 'test',
        'title': 'Tests',
        'assignments': [{
            'id': test_test_material['assignment_id'],
            'title': '1. uzdevums',
            'description': 'Apraksts',
            'max_points': 15,
            'questions': [
                {
                    'id': test_test_material['question_id'],
                    'question_text': 'Kas ir Python?',
                    'question_type': 'short_answer',
                    'correct_answer': 'Atbilde',
                    'points': 5,
                    'options': []
                },
                {
                    # Jauns jautājums bez id
                    'question_text': 'Jauns jautājums?',
                    'question_type': 'true_false',
                    'correct_answer': 'True',
                    'points': 10,
                    'options': []
                }
            ]
        }]
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda ka jautājums ir pievienots
    with app.app_context():
        test = Test.query.get(test_test_material['test_id'])
        assert test is not None, "Testam būtu jābūt DB"
        assert len(test.assignments[0].questions) == 2, "Uzdevumam jābūt 2 jautājumiem"
        assert test.assignments[0].questions[1].question_text == 'Jauns jautājums?', \
            "Jaunajam jautājumam jābūt ar pareizu tekstu"
