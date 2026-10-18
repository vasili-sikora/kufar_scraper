import logging
from pathlib import Path
from typing import Literal

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"


def setup_logging(interface: Literal["cli", "telegram"]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOGS_DIR / f"{interface}.log",
        encoding="utf-8",
        level=logging.INFO,
        format=("%(asctime)s | %(levelname)s | %(name)s | %(message)s"),
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
