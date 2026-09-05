import httpx
import re
from bs4 import BeautifulSoup
import asyncio


class HttpKufarClient:
    def __init__(self, session: httpx.AsyncClient):
        self._session = session

    async def _get_user_page(self) -> str:
        response = await self._session.get(self._session.base_url)

        return response.text

    async def _get_announcements_links(self) -> list[str]:
        raw_page = await self._get_user_page()
        links = re.findall(r'"adViewLink":"([^"]*)"', raw_page)

        return links

    async def _get_announcement_data(self, link: str) -> dict:
        response = await self._session.get(link)
        raw = response.text
        data = {}
        price = re.findall(r'"price":.*?}', raw)
        data["price"] = price[0].split('"')[3]
        title = re.findall(r'"title":.*?}', raw)
        data["title"] = title[0].split('"')[3]
        description = re.findall(r'"description":.*?}', raw)
        data["description"] = description[0].split('"')[3]

        return data

    async def get_announcements_data(self) -> list[dict]:
        links = await self._get_announcements_links()
        data = await asyncio.gather(
            *[self._get_announcement_data(link) for link in links]
        )

        return data
