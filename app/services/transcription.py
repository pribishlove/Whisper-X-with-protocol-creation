import tempfile, time, io, gc
import torch
import whisperx
from app.core.config import settings

def clear_memory():
    if settings.USE_GC:
        gc.collect()
        torch.cuda.empty_cache()

def run_transcription(audio_bytes: bytes) -> str:
    start = time.time()

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    model = whisperx.load_model(
        whisper_arch=settings.WHISPER_MODEL,
        device=settings.DEVICE,
        language=settings.LANGUAGE_CODE,
        compute_type=settings.COMPUTE_TYPE
    )
    audio = whisperx.load_audio(tmp_path)
    transcription = model.transcribe(audio)
    clear_memory()

    align_model, metadata = whisperx.load_align_model(
        language_code=settings.LANGUAGE_CODE, device=settings.DEVICE
    )
    aligned = whisperx.align(transcription["segments"], align_model, metadata, audio, settings.DEVICE)
    clear_memory()

    diarize_model = whisperx.DiarizationPipeline(
        use_auth_token=settings.HUGGINGFACE_TOKEN, device=settings.DEVICE
    )
    diarization = diarize_model(audio, min_speakers=settings.MIN_SPEAKERS, max_speakers=settings.MAX_SPEAKERS)
    final_result = whisperx.assign_word_speakers(diarization, aligned)

    text_output = io.StringIO()
    for segment in final_result["segments"]:
        speaker = segment.get("speaker", "Unknown")
        text_output.write(f"[{segment['start']:.2f}s - {segment['end']:.2f}s] Speaker {speaker}: {segment['text']}\n")

    print(f"✅ Transcription completed in {time.time() - start:.2f} seconds")
    return text_output.getvalue()
