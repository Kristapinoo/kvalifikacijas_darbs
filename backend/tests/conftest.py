"""
Test Configuration and Fixtures
Pytest konfigurācija un fixtures visiem testiem
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app
from extensions import db, bcrypt
from models import User, Test, StudyMaterial, Assignment, Question, QuestionOption


@pytest.fixture
def app():
    """Izveido Flask aplikāciju test režīmā"""
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test_key',
        'WTF_CSRF_ENABLED': False
    })

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client HTTP pieprasījumiem"""
    return app.test_client()


@pytest.fixture
def test_db(app):
    """Tīra test datu bāze"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_user(app, test_db):
    """Test lietotājs"""
    with app.app_context():
        password_hash = bcrypt.generate_password_hash('test_password').decode('utf-8')
        user = User(
            email='test@test.lv',
            password_hash=password_hash
        )
        db.session.add(user)
        db.session.commit()
        # Refresh to get id
        db.session.refresh(user)
        user_id = user.id
        user_email = user.email
    return {'id': user_id, 'email': user_email, 'password': 'test_password'}


@pytest.fixture
def auth_client(client, test_user):
    """Autentificēts client"""
    client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    return client


@pytest.fixture
def test_test_material(app, test_user):
    """Test materiāls (tests)"""
    with app.app_context():
        test = Test(
            title='Test materiāls',
            user_id=test_user['id']
        )
        db.session.add(test)
        db.session.commit()

        assignment = Assignment(
            test_id=test.id,
            title='1. uzdevums',
            description='Uzdevuma apraksts',
            max_points=10,
            order_number=1
        )
        db.session.add(assignment)
        db.session.commit()

        question = Question(
            assignment_id=assignment.id,
            question_text='Kas ir Python?',
            question_type='multiple_choice',
            correct_answer='A',
            points=5,
            order_number=1
        )
        db.session.add(question)
        db.session.commit()

        option = QuestionOption(
            question_id=question.id,
            option_text='Programmēšanas valoda',
            is_correct=True,
            order_number=1
        )
        db.session.add(option)
        db.session.commit()

        db.session.refresh(test)
        test_id = test.id
        assignment_id = assignment.id
        question_id = question.id

    return {
        'test_id': test_id,
        'assignment_id': assignment_id,
        'question_id': question_id
    }


@pytest.fixture
def test_study_material(app, test_user):
    """Test mācību materiāls"""
    import json
    with app.app_context():
        material = StudyMaterial(
            title='Mācību materiāls',
            user_id=test_user['id'],
            content=json.dumps({
                'summary': '<p>Kopsavilkums</p>',
                'terms': [
                    {'name': 'Termins 1', 'definition': 'Definīcija 1'}
                ]
            })
        )
        db.session.add(material)
        db.session.commit()
        db.session.refresh(material)
        material_id = material.id

    return {'material_id': material_id}
