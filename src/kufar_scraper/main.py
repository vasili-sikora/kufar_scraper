import asyncio
import os

import httpx
from dotenv.main import load_dotenv

from kufar_scraper.cli import update_advertisements_in_db
from kufar_scraper.kufar.client import HttpKufarClient

load_dotenv()
URL = os.getenv("USER_URL")


async def main():
    if not URL:
        raise ValueError("USER_URL is not set in .env")

    await update_advertisements_in_db()


if __name__ == "__main__":
    asyncio.run(main())
