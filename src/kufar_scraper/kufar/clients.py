import asyncio
import json
import re
from json.decoder import JSONDecodeError

import httpx

from kufar_scraper.config import load_config
from kufar_scraper.kufar.dto import AdvertisementDto


class HttpKufarClient:
    def __init__(self, session: httpx.AsyncClient):
        self._session = session

    async def _get_user_page(self, user_page_url: str) -> str:
        response = await self._session.get(user_page_url)
        if response.status_code != 200:
            raise ConnectionError("Не удалось получить страницу пользователя")

        page_html = response.text

        return page_html

    async def _get_announcements_links(self, user_page_url: str) -> list[str]:
        raw_page = await self._get_user_page(user_page_url)
        links = re.findall(r'"adViewLink":"([^"]*)"', raw_page)

        return links

    async def _get_announcement_data(self, link: str) -> AdvertisementDto:
        response: httpx.Response = await self._session.get(link)
        if response.status_code == 429:
            raise ConnectionError(
                "Скорее всего, у вас включен VPN. Попробуйте отключить его и повторить попытку"
            )
        if response.status_code != 200:
            raise ConnectionError("Не удалось получить данные объявления")

        raw = response.text
        ad_id = re.findall(r'"adId":.*?}', raw)[0].split('"')[3]
        price = re.findall(r'"price":.*?}', raw)[0].split('"')[3]
        title = re.findall(r'"title":.*?}', raw)[0].split('"')[3]
        description = re.findall(r'"description":.*?}', raw)[0].split('"')[3]

        advertisement = AdvertisementDto(
            kufar_id=ad_id, title=str(title), description=str(description), price=str(price), url=link
        )

        return advertisement

    async def get_announcements_data(self, user_page_url: str) -> list[AdvertisementDto]:
        links = await self._get_announcements_links(user_page_url)
        if not links:
            raise ValueError("Не удалось найти объявления")

        data = await asyncio.gather(
            *[self._get_announcement_data(link) for link in links]
        )

        return data

    async def get_api_advertisements_data(self, url: str) -> list[AdvertisementDto]:
        try:
            response = await self._session.get(url, headers={"Authorization": load_config().BEARER_TOKEN})
        except httpx.TimeoutException:
            raise ValueError("Превышено время ожидания")

        response_text = response.text

        try:
            advertisements_data = json.loads(response_text)
        except JSONDecodeError:
            raise ValueError("Не удалось декодировать JSON")

        advertisements_dto = []
        for ad in advertisements_data["ads"]:
            ad_id = ad["ad_id"]
            title = ad["subject"]
            price = int(ad["price_byn"])/100
            url = ad["link"]
            advertisements_dto.append(AdvertisementDto(kufar_id=ad_id, title=title, description="", price=str(price), url=url))

        return advertisements_dto
