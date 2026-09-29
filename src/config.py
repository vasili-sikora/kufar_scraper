import os

from dotenv import load_dotenv

_ = load_dotenv()

DB_URL = os.getenv("DB_URL", "sqlite:///kufar.db")
KUFAR_TOKEN = os.getenv("KUFAR_TOKEN", "")
