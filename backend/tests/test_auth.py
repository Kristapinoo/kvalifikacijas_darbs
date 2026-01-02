"""
MODUĻA 1: Autentifikācijas testi
6 testi lietotāja reģistrācijai, pieteikšanās un atteikšanās
"""
import pytest
from models import User


def test_01_registration_success(client, test_db):
    """
    Nr: 1
    Testējamā funkcionalitāte: Lietotāja reģistrācija ar derīgiem datiem
    Sagaidamais rezultāts: Lietotājs tiek izveidots datu bāzē ar šifrētu paroli
    """
    # ACTION - izpilda HTTP pieprasījumu
    response = client.post('/api/auth/register', json={
        'email': 'jauns@test.lv',
        'password': 'parole123'
    })

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 201, "Statuss būtu jābūt 201"
    assert 'user' in response.json, "Atbildē jābūt 'user'"

    # DB CHECK - pārbauda datu bāzi
    user = User.query.filter_by(email='jauns@test.lv').first()
    assert user is not None, "Lietotājam būtu jābūt DB"
    from extensions import bcrypt
    assert bcrypt.check_password_hash(user.password_hash, 'parole123'), "Parolei jābūt korekti šifrētai"


def test_02_registration_duplicate_email(client, test_user):
    """
    Nr: 2
    Testējamā funkcionalitāte: Reģistrācija ar jau eksistējošu e-pastu
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "Šis e-pasts jau ir reģistrēts"
    """
    # ACTION - mēģina reģistrēties ar esošu e-pastu
    response = client.post('/api/auth/register', json={
        'email': test_user['email'],
        'password': 'parole123'
    })

    # ASSERT - pārbauda kļūdu
    assert response.status_code in [400, 409], "Statuss būtu jābūt 400 vai 409"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    assert 'already exists' in response.json['error'].lower() or 'jau' in response.json['error'].lower(), \
        "Kļūdas ziņojumā jābūt informācijai par eksistējošu e-pastu"


def test_03_registration_short_password(client, test_db):
    """
    Nr: 3
    Testējamā funkcionalitāte: Reģistrācija ar pārāk īsu paroli
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "Parolei jābūt vismaz 6 rakstzīmes garai"
    """
    # ACTION - mēģina reģistrēties ar īsu paroli
    response = client.post('/api/auth/register', json={
        'email': 'test@test.lv',
        'password': '123'
    })

    # ASSERT - pārbauda kļūdu
    assert response.status_code == 400, "Statuss būtu jābūt 400"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    assert '6' in response.json['error'] or 'least' in response.json['error'].lower(), \
        "Kļūdas ziņojumā jābūt informācijai par minimālo garumu"


def test_04_login_success(client, test_user):
    """
    Nr: 4
    Testējamā funkcionalitāte: Lietotāja pieteikšanās ar pareiziem datiem
    Sagaidamais rezultāts: Lietotājs tiek pieteikts un sesija izveidota
    """
    # ACTION - pieteicas ar pareiziem datiem
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': test_user['password']
    })

    # ASSERT - pārbauda veiksmīgu pieteikšanos
    assert response.status_code == 200, "Statuss būtu jābūt 200"
    assert 'user' in response.json, "Atbildē jābūt 'user'"
    assert response.json['user']['email'] == test_user['email'], "E-pastam jāsakrīt"


def test_05_login_wrong_password(client, test_user):
    """
    Nr: 5
    Testējamā funkcionalitāte: Pieteikšanās ar nepareizu paroli
    Sagaidamais rezultāts: Tiek atgriezts kļūdas ziņojums "Nepareizs e-pasts vai parole"
    """
    # ACTION - pieteicas ar nepareizu paroli
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': 'nepareiza_parole'
    })

    # ASSERT - pārbauda kļūdu
    assert response.status_code == 401, "Statuss būtu jābūt 401"
    assert 'error' in response.json, "Atbildē jābūt 'error'"
    error_msg = response.json['error'].lower()
    assert 'incorrect' in error_msg or 'invalid' in error_msg or 'nepareiz' in error_msg, \
        "Kļūdas ziņojumā jābūt informācijai par nepareiziem datiem"


def test_06_logout(auth_client):
    """
    Nr: 6
    Testējamā funkcionalitāte: Lietotāja atteikšanās
    Sagaidamais rezultāts: Sesija tiek iznīcināta
    """
    # ACTION - atteicas
    response = auth_client.post('/api/auth/logout')

    # ASSERT - pārbauda veiksmīgu atteikšanos
    assert response.status_code == 200, "Statuss būtu jābūt 200"
