from datetime import UTC, datetime
from random import uniform
from time import sleep

import httpx

from config import KUFAR_TOKEN
from schemas import AdvertisementItem

KUFAR_URL = "https://api.kufar.by"
MY_ITEMS_URL = "my-items-v2/v1/items"


class KufarClient:
    def __init__(
        self,
        token: str = KUFAR_TOKEN,
        session: httpx.Client = None,
    ):
        self._session: httpx.Client = session or httpx.Client(
            headers={"Authorization": token if token.startswith("Bearer ") else f"Bearer {token}"},
            timeout=15,
            follow_redirects=True,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_my_items(self) -> list[AdvertisementItem]:
        url = f"{KUFAR_URL}/{MY_ITEMS_URL}"
        response = self._session.get(url)
        response.raise_for_status()

        data = response.json()
        ads_raw = data.get("ads", [])

        parsed_items: list[AdvertisementItem] = []
        for ad in ads_raw:
            price_raw = ad.get("price_byn", "0")
            price = round(int(price_raw) / 100.0, 2) if price_raw.isdigit() else 0.0

            raw_date = ad.get("list_time") or ad.get("start_time")
            pub_date = datetime.fromisoformat(raw_date) if raw_date else datetime.now(tz=UTC)

            parsed_items.append(
                AdvertisementItem(
                    kufar_id=int(ad["ad_id"]),
                    title=ad["subject"],
                    price=price,
                    status=ad["ad_status"],
                    link=ad.get("link", ""),
                    published_at=pub_date,
                )
            )

        return parsed_items

    def get_item_page_html(self, item_url: str) -> str:
        if not item_url:
            return ""

        sleep(uniform(0.8, 1.8))
        try:
            response = self._session.get(item_url)
            response.raise_for_status()
            page_html = response.text
            return page_html
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return ""
            raise
