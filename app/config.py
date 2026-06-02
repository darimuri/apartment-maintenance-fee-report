import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
BASE_DIR.mkdir(exist_ok=True)
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Test mode: set TEST_DB_PATH env var to use separate test database
TEST_DB_PATH = os.getenv("TEST_DB_PATH", "")
if TEST_DB_PATH:
    DB_PATH = TEST_DB_PATH
else:
    DB_PATH = str(DATA_DIR / "management_fees.db")

UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "qwen/qwen3-vl-32b-instruct"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

MINIMAX_API_KEY = os.getenv("OPENAI_API_KEY", "")
MINIMAX_API_URL = os.getenv("OPENAI_BASE_URL", "https://api.minimax.io/v1") + "/chat/completions"
MINIMAX_MODEL = os.getenv("OPENAI_MODEL", "MiniMax-M2.7")

OCR_PROMPT = "이 이미지에서 텍스트를 모두 추출해주세요."
