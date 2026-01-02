"""
MODUĻA 4: Vēstures testi
5 testi materiālu saraksta skatīšanai, ielādei un dzēšanai
"""
import pytest
from models import Test, StudyMaterial, User
from extensions import db, bcrypt


def test_01_get_materials_list(auth_client, test_test_material, test_study_material):
    """
    Nr: 1
    Testējamā funkcionalitāte: Lietotāja materiālu saraksta iegūšana
    Sagaidamais rezultāts: Tiek atgriezts saraksts ar visiem lietotāja materiāliem
    """
    # ACTION - iegūst materiālu sarakstu
    response = auth_client.get('/api/materials')

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"
    assert 'materials' in response.json, "Atbildē jābūt 'materials'"
    assert len(response.json['materials']) >= 2, "Sarakstā jābūt vismaz 2 materiāliem"

    # Pārbauda materiālu tipus
    material_types = [m['type'] for m in response.json['materials']]
    assert 'test' in material_types, "Sarakstā jābūt testam"
    assert 'study_material' in material_types, "Sarakstā jābūt mācību materiālam"


def test_02_load_material(auth_client, test_test_material):
    """
    Nr: 2
    Testējamā funkcionalitāte: Konkrēta materiāla ielāde ar visiem datiem
    Sagaidamais rezultāts: Tiek atgriezts pilns materiāls ar uzdevumiem un jautājumiem
    """
    # ACTION - ielādē testu
    response = auth_client.get(f'/api/materials/{test_test_material["test_id"]}?type=test')

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"
    assert 'id' in response.json, "Atbildē jābūt 'id'"
    assert response.json['id'] == test_test_material['test_id'], "ID jāsakrīt"
    assert 'assignments' in response.json, "Atbildē jābūt 'assignments'"
    assert len(response.json['assignments']) > 0, "Testam jābūt uzdevumiem"

    # Pārbauda uzdevuma struktūru
    assignment = response.json['assignments'][0]
    assert 'questions' in assignment, "Uzdevumam jābūt jautājumiem"
    assert len(assignment['questions']) > 0, "Uzdevumam jābūt vismaz 1 jautājumam"


def test_03_delete_material(auth_client, test_test_material, app):
    """
    Nr: 3
    Testējamā funkcionalitāte: Materiāla dzēšana
    Sagaidamais rezultāts: Materiāls tiek veiksmīgi izdzēsts no datu bāzes
    """
    # ACTION - dzēš materiālu
    response = auth_client.delete(f'/api/materials/{test_test_material["test_id"]}?type=test')

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"

    # DB CHECK - pārbauda ka materiāls ir dzēsts
    with app.app_context():
        test = Test.query.get(test_test_material['test_id'])
        assert test is None, "Testam nevajadzētu būt DB pēc dzēšanas"


def test_04_get_nonexistent(auth_client):
    """
    Nr: 4
    Testējamā funkcionalitāte: Neeskoša materiāla ielādes mēģinājums
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "Material not found"
    """
    # ACTION - mēģina ielādēt neesošu materiālu
    response = auth_client.get('/api/materials/99999?type=test')

    # ASSERT - pārbauda kļūdu
    assert response.status_code == 404, "Statuss būtu jābūt 404"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    assert 'not found' in response.json['error'].lower(), \
        "Kļūdas ziņojumā jābūt informācijai par neatrasto materiālu"


def test_05_access_other_user(app, test_db, client, test_test_material):
    """
    Nr: 5
    Testējamā funkcionalitāte: Mēģinājums piekļūt cita lietotāja materiālam
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "Material not found"
    """
    # SETUP - izveido otru lietotāju
    with app.app_context():
        password_hash = bcrypt.generate_password_hash('other_password').decode('utf-8')
        other_user = User(
            email='other@test.lv',
            password_hash=password_hash
        )
        db.session.add(other_user)
        db.session.commit()

    # ACTION - pieteicas kā otrais lietotājs
    client.post('/api/auth/login', json={
        'email': 'other@test.lv',
        'password': 'other_password'
    })

    # Mēģina piekļūt pirmā lietotāja materiālam
    response = client.get(f'/api/materials/{test_test_material["test_id"]}?type=test')

    # ASSERT - pārbauda ka piekļuve ir liegta
    assert response.status_code == 404, "Statuss būtu jābūt 404"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    assert 'not found' in response.json['error'].lower(), \
        "Kļūdas ziņojumā jābūt informācijai ka materiāls nav atrasts"
