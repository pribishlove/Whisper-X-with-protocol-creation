# app/main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile

from .core.config import settings
from .services.transcription import run_transcription
from .services.protocol import run_llama_protocol

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    audio_bytes = await file.read()

    transcribed_text = run_transcription(audio_bytes)
    protocol = run_llama_protocol(transcribed_text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(protocol)
        tmp_path = tmp.name

    return FileResponse(tmp_path, media_type="text/plain", filename="protocol.txt")
