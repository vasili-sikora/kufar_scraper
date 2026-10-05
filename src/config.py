import os
from pathlib import Path

from dotenv import load_dotenv

_ = load_dotenv()

KUFAR_TOKEN = os.getenv("KUFAR_TOKEN", "")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_PATH = DATA_DIR / "kufar.db"
DB_URL = os.getenv("DB_URL", f"sqlite:///{DB_PATH}")
LOGS_FILEPATH = Path(__file__).resolve().parent.parent / "logs.log"
