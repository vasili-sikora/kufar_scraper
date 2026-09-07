import asyncio
import re

import httpx

from kufar_scraper.kufar.dto import Advertisement


class HttpKufarClient:
    def __init__(self, session: httpx.AsyncClient, user_url: str):
        self._session = session
        self._user_url = user_url

    async def _get_user_page(self) -> str:
        response = await self._session.get(self._user_url)
        if response.status_code != 200:
            raise ConnectionError("Не удалось получить страницу пользователя")

        page_html = response.text
        print(page_html)
        return page_html

    async def _get_announcements_links(self) -> list[str]:
        raw_page = await self._get_user_page()
        links = re.findall(r'"adViewLink":"([^"]*)"', raw_page)
        print(links)
        return links

    async def _get_announcement_data(self, link: str) -> Advertisement:
        response: httpx.Response = await self._session.get(link)
        if response.status_code == 429:
            raise ConnectionError(
                "Скорее всего, у вас включен VPN. Попробуйте отключить его и повторить попытку"
            )
        if response.status_code != 200:
            raise ConnectionError("Не удалось получить данные объявления")

        raw = response.text
        price = re.findall(r'"price":.*?}', raw)[0].split('"')[3]
        title = re.findall(r'"title":.*?}', raw)[0].split('"')[3]
        description = re.findall(r'"description":.*?}', raw)[0].split('"')[3]

        advertisement = Advertisement(
            title=str(title), description=str(description), price=str(price), url=link
        )

        return advertisement

    async def get_announcements_data(self) -> list[Advertisement]:
        links = await self._get_announcements_links()
        if not links:
            raise ValueError("Не удалось найти объявления")

        data = await asyncio.gather(
            *[self._get_announcement_data(link) for link in links]
        )
        print(data)
        return data
