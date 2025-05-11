import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

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
