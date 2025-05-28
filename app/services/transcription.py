import tempfile, time, io, gc
#import torch
#import whisperx
from app.core.config import settings
#from whisperx.diarize import DiarizationPipeline

def clear_memory():
    if settings.USE_GC:
        gc.collect()
        torch.cuda.empty_cache()

def run_transcription(audio_bytes: bytes) -> str:
    """
    Мок-версия транскрибации. Возвращает фиксированный текст вместо реальной транскрибации.
    """
    return "Тут была транскрибация аудио файла"
