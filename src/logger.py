import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

from config import ENABLE_CLI_LOGS

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"

MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB


def setup_logging(interface: Literal["cli", "telegram", "cron"]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file = LOGS_DIR / f"{interface}.log"
    file_handler = RotatingFileHandler(
        filename=file,
        maxBytes=MAX_LOG_SIZE,
        backupCount=3,
        encoding="utf-8",
    )

    handlers: list[logging.Handler] = [file_handler]

    if ENABLE_CLI_LOGS or os.getenv("RAILWAY_ENVIRONMENT"):
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        handlers=handlers,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
