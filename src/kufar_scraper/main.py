import asyncio
import os

import httpx
from dotenv.main import load_dotenv

from kufar_scraper.kufar.client import HttpKufarClient

load_dotenv()
URL = os.getenv("USER_URL")

async def main():
    if not URL:
        raise ValueError("USER_URL not set in .env")

    async with httpx.AsyncClient(base_url=URL) as session:
        c = HttpKufarClient(session)

        all_data = await c.get_announcements_data()
        print(all_data)

        for adv in all_data:
            for k, v in adv.items():
                print(k, v)


if __name__ == "__main__":
    asyncio.run(main())
