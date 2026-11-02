import argparse
import logging
import subprocess
import sys
from pathlib import Path

from cli import cli
from client import KufarClient
from db import init_db
from dependencies import get_service
from exceptions import KufarScraperError
from exporters import GoogleSheetsExporter
from logger import setup_logging

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Kufar Scraper runner")
    parser.add_argument(
        "--cron",
        action="store_true",
        help="Run the script in cron mode (without Telegram bot and CLI)",
    )
    return parser.parse_args()


def run_interactive() -> None:
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


def run_cron() -> None:
    setup_logging("cron")
    init_db()
    logger.info("Starting cron job...")

    try:
        with get_service() as service, KufarClient() as client:
            service.sync_ads_to_db(client)
            service.export_ads(GoogleSheetsExporter())
        logger.info("Cron job completed successfully.")
    except KufarScraperError:
        logger.exception("An error occurred during the cron job.")
        sys.exit(1)


def main() -> None:
    args = parse_args()
    if args.cron:
        run_cron()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
