import os
from pathlib import Path

from dotenv import load_dotenv

_ = load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
KUFAR_TOKEN = os.getenv("KUFAR_TOKEN", "")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True, parents=True)
DB_PATH = DATA_DIR / "kufar.db"
DB_URL = os.getenv("DB_URL", f"sqlite:///{DB_PATH}")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0"))

GOOGLE_SERVICE_ACCOUNT_FILE = Path(
    os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", str(BASE_DIR / "google_credentials.json"))
)
GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
