import pytest
from app.services.transcription import run_transcription
from app.services.protocol import run_llama_protocol


@pytest.mark.parametrize("input_audio", [
    b'', 
    b'test audio content',
])
def test_transcription_service(input_audio):
    result = run_transcription(input_audio)
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.parametrize("input_text,expected_sections", [
    ("", ["ПРОТОКОЛ СОВЕЩАНИЯ", "Дата:", "Время:", "ПРИСУТСТВУЮЩИЕ:", "ПОВЕСТКА ДНЯ:", "РЕШЕНИЯ:"]),
    ("Тестовый текст", ["ПРОТОКОЛ СОВЕЩАНИЯ", "Дата:", "Время:", "ПРИСУТСТВУЮЩИЕ:", "ПОВЕСТКА ДНЯ:", "РЕШЕНИЯ:"]),
])
def test_protocol_sections(input_text, expected_sections):
    result = run_llama_protocol(input_text)
    for section in expected_sections:
        assert section in result 