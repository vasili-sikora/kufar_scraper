import logging
import subprocess
import sys
from pathlib import Path

from cli import cli
from db import init_db
from logger import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging("cli")
    logger.info("Starting application...")
    init_db()

    bot_path = Path(__file__).resolve().with_name("telegram.py")
    bot_process = subprocess.Popen([sys.executable, str(bot_path)])

    try:
        cli()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down...")
        print("\nShutting down...")
    finally:
        if bot_process.poll() is None:
            bot_process.terminate()

        try:
            bot_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            bot_process.kill()
            bot_process.wait()


if __name__ == "__main__":
    main()
