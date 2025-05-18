import os
import pathlib
from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

# Считываем параметры по отдельности
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "admin")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "whisperdb")

# Собираем строку подключения
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Settings:
    DEVICE = "cuda"
    USE_GC = True
    LANGUAGE_CODE = "ru"
    WHISPER_MODEL = "turbo"
    COMPUTE_TYPE = "float16"
    MIN_SPEAKERS = 1
    MAX_SPEAKERS = 3
    MODEL_PATH = BASE_DIR / "models" / "llama-3-8B-Instruct.Q4_K_M.gguf"
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

settings = Settings()
