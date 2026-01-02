"""
MODUĻA 5: Eksporta testi
3 testi PDF un DOCX eksportam
"""
import pytest
from io import BytesIO


def test_01_export_pdf_with_answers(auth_client, test_test_material):
    """
    Nr: 1
    Testējamā funkcionalitāte: Testa eksportēšana uz PDF ar atbildēm
    Sagaidamais rezultāts: Tiek ģenerēts PDF fails ar jautājumiem un pareizajām atbildēm
    """
    # ACTION - eksportē PDF ar atbildēm
    response = auth_client.get(
        f'/api/export/pdf/{test_test_material["test_id"]}?type=test&include_answers=true'
    )

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"
    assert response.content_type == 'application/pdf', "Content-Type jābūt application/pdf"
    assert len(response.data) > 0, "PDF failam jābūt ar saturu"

    # Pārbauda ka response ir derīgs PDF
    assert response.data[:4] == b'%PDF', "Failam jāsākas ar PDF signatūru"


def test_02_export_pdf_without_answers(auth_client, test_test_material):
    """
    Nr: 2
    Testējamā funkcionalitāte: Testa eksportēšana uz PDF bez atbildēm (skolēniem)
    Sagaidamais rezultāts: Tiek ģenerēts PDF fails tikai ar jautājumiem, bez pareizajām atbildēm
    """
    # ACTION - eksportē PDF bez atbildēm
    response = auth_client.get(
        f'/api/export/pdf/{test_test_material["test_id"]}?type=test&include_answers=false'
    )

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"
    assert response.content_type == 'application/pdf', "Content-Type jābūt application/pdf"
    assert len(response.data) > 0, "PDF failam jābūt ar saturu"

    # Pārbauda ka response ir derīgs PDF
    assert response.data[:4] == b'%PDF', "Failam jāsākas ar PDF signatūru"

    # Pārbauda ka fails nav tukšs un ir mazāks par versiju ar atbildēm
    # (bez atbildēm būs mazāks faila izmērs)
    with_answers = auth_client.get(
        f'/api/export/pdf/{test_test_material["test_id"]}?type=test&include_answers=true'
    )
    assert len(response.data) <= len(with_answers.data), \
        "PDF bez atbildēm vajadzētu būt mazākam vai vienādam ar versiju ar atbildēm"


def test_03_export_docx(auth_client, test_test_material):
    """
    Nr: 3
    Testējamā funkcionalitāte: Testa eksportēšana uz DOCX formātu
    Sagaidamais rezultāts: Tiek ģenerēts DOCX fails ar testu
    """
    # ACTION - eksportē DOCX
    response = auth_client.get(
        f'/api/export/docx/{test_test_material["test_id"]}?type=test&include_answers=true'
    )

    # ASSERT - pārbauda rezultātu
    assert response.status_code == 200, "Statuss būtu jābūt 200"
    assert 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in response.content_type, \
        "Content-Type jābūt DOCX"
    assert len(response.data) > 0, "DOCX failam jābūt ar saturu"

    # Pārbauda ka response ir derīgs DOCX (ZIP arhīvs)
    assert response.data[:2] == b'PK', "DOCX failam jāsākas ar ZIP signatūru (PK)"
