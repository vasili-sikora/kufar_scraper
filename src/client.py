from datetime import datetime
from random import uniform
from time import sleep

import httpx

from config import KUFAR_TOKEN
from schemas import AdvertisementItem


class KufarClient:
    def __init__(
        self,
        token: str = KUFAR_TOKEN,
        base_url: str = "https://api.kufar.by",
        timeout: float = 15.0,
    ):
        self._base_url = base_url.rstrip("/")
        self._session: httpx.Client = httpx.Client(
            headers={"Authorization": token if token.startswith("Bearer ") else f"Bearer {token}"},
            timeout=timeout,
            follow_redirects=True,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_my_items(self) -> list[AdvertisementItem]:
        url = f"{self._base_url}/my-items-v2/v1/items"
        response = self._session.get(url)
        response.raise_for_status()

        data = response.json()
        ads_raw = data.get("ads", [])

        parsed_items: list[AdvertisementItem] = []
        for ad in ads_raw:
            price = round(int(ad["price_byn"]) / 100.0, 2)
            date = datetime.fromisoformat(ad["date"])
            parsed_items.append(
                AdvertisementItem(
                    kufar_id=int(ad["ad_id"]),
                    title=ad["subject"],
                    price=price,
                    status=ad["ad_status"],
                    link=ad["link"],
                    published_at=date,
                )
            )

        return parsed_items

    def get_item_page_html(self, item_url: str) -> str:
        if not item_url:
            return ""

        sleep(uniform(0.7, 1.5))
        try:
            response = self._session.get(item_url)
            response.raise_for_status()
            page_html = response.text
            return page_html
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return ""
            raise
