import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging(interface: Literal["cli", "telegram"]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    file = LOGS_DIR / f"{interface}.log"
    file_handler = RotatingFileHandler(
        filename=file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )

    logging.basicConfig(
        handlers=[file_handler],
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
