import html
import re
from datetime import UTC, datetime
from random import uniform
from time import sleep

import httpx

from schemas import AdvertisementItem


class KufarClient:
    def __init__(self, token: str, base_url: str = "https://api.kufar.by"):
        self._base_url = base_url.rstrip("/")
        self._session: httpx.Client = httpx.Client(
            headers={
                "Authorization": token
                if token.startswith("Bearer ")
                else f"Bearer {token}"
            },
            timeout=15,
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
            price_raw = ad.get("price_byn", "0")
            price = round(int(price_raw) / 100.0, 2) if price_raw.isdigit() else 0.0

            raw_date = ad.get("list_time") or ad.get("start_time")
            pub_date = (
                datetime.fromisoformat(raw_date) if raw_date else datetime.now(tz=UTC)
            )

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

    def get_item_description(self, item_url: str) -> str:
        if not item_url:
            return ""

        try:
            sleep(uniform(1.0, 2.0))
            response = self._session.get(item_url)
            response.raise_for_status()
            page_html = response.text

            match = re.search(
                r'item[Pp]rop=["\']description["\'][^>]*>(.*?)</div>',
                page_html,
                re.DOTALL,
            )
            if not match:
                return ""

            raw_text = match.group(1)
            text_with_newlines = re.sub(r"<br\s*/?>|</p>", "\n", raw_text)
            clean_text = re.sub(r"<[^>]+>", "", text_with_newlines)
            decoded_text = html.unescape(clean_text)

            return decoded_text.strip()
        except httpx.HTTPError as e:
            print(f"Не удалось получить описание для {item_url}: {e}")
            return ""
