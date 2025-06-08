import pytest
from app.services.transcription import run_transcription
from app.services.protocol import run_llama_protocol

def test_transcription_service():
    # Тест с пустыми байтами
    empty_audio = b''
    result = run_transcription(empty_audio)
    assert isinstance(result, str)
    assert len(result) > 0

    # Тест с непустыми байтами
    test_audio = b'test audio content'
    result = run_transcription(test_audio)
    assert isinstance(result, str)
    assert len(result) > 0

def test_protocol_service():
    # Тест с пустым текстом
    empty_text = ""
    result = run_llama_protocol(empty_text)
    assert isinstance(result, str)
    assert "ПРОТОКОЛ СОВЕЩАНИЯ" in result
    assert "Дата:" in result
    assert "Время:" in result

    # Тест с реальным текстом
    test_text = "Обсуждение проекта и планирование задач"
    result = run_llama_protocol(test_text)
    assert isinstance(result, str)
    assert "ПРОТОКОЛ СОВЕЩАНИЯ" in result
    assert "ПРИСУТСТВУЮЩИЕ:" in result
    assert "ПОВЕСТКА ДНЯ:" in result
    assert "РЕШЕНИЯ:" in result

@pytest.mark.parametrize("input_text,expected_sections", [
    ("", ["ПРОТОКОЛ СОВЕЩАНИЯ", "Дата:", "Время:", "ПРИСУТСТВУЮЩИЕ:", "ПОВЕСТКА ДНЯ:", "РЕШЕНИЯ:"]),
    ("Тестовый текст", ["ПРОТОКОЛ СОВЕЩАНИЯ", "Дата:", "Время:", "ПРИСУТСТВУЮЩИЕ:", "ПОВЕСТКА ДНЯ:", "РЕШЕНИЯ:"]),
])
def test_protocol_sections(input_text, expected_sections):
    result = run_llama_protocol(input_text)
    for section in expected_sections:
        assert section in result 