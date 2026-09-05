import asyncio
import os

from dotenv.main import load_dotenv
import requests
import re
from bs4 import BeautifulSoup
import httpx
import dotenv
from kufar_scraper.kufar.client import HttpKufarClient


load_dotenv()
URL = os.getenv("USER_URL")



async def main():
    if not URL:
        raise ValueError("USER_URL not set in .env")

    c = HttpKufarClient(httpx.AsyncClient(base_url=URL))

    all_data = await c.get_announcements_data()
    print(all_data)

    for adv in all_data:
        print(adv)


if __name__ == "__main__":
    asyncio.run(main())
