from fastapi import FastAPI, UploadFile, File, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
from fastapi.responses import JSONResponse
from app.db.database import Base, engine, SessionLocal
from app.api import routes_auth, routes_protected
from app.core.config import settings
from app.services.transcription import run_transcription
from app.services.protocol import run_llama_protocol
from app.core.auth import get_user_from_token
from app.core.deps import oauth2_scheme
from app.api import routes_frontend

app = FastAPI()

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(routes_frontend.router)
app.include_router(routes_auth.router, prefix="/auth", tags=["auth"])
app.include_router(routes_protected.router, prefix="/users", tags=["users"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/process")
async def process_file(
    request: Request,
    file: UploadFile = File(...)
):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = SessionLocal()
    try:
        user = get_user_from_token(token, db)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    if user.requests_left <= 0:
        return JSONResponse(
            status_code=403,
            content={"detail": "Request limit exceeded. Only 20 allowed."}
        )

    user.requests_left -= 1
    db.commit()

    audio_bytes = await file.read()
    transcribed_text = run_transcription(audio_bytes)
    protocol = run_llama_protocol(transcribed_text)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8") as tmp:
        tmp.write(protocol)
        tmp_path = tmp.name

    return FileResponse(tmp_path, media_type="text/plain", filename="protocol.txt")
