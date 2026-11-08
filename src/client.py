import logging
from datetime import UTC, datetime
from random import uniform
from time import sleep

import httpx

from config import KUFAR_TOKEN
from schemas import AdvertisementDto

KUFAR_URL = "https://api.kufar.by"
MY_ITEMS_URL = "my-items-v2/v1/items"
logger = logging.getLogger(__name__)


class KufarClient:
    def __init__(
        self,
        token: str = KUFAR_TOKEN,
        base_url: str = KUFAR_URL,
        timeout: float = 15.0,
        session: httpx.Client | None = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._session: httpx.Client = session or httpx.Client(
            headers={"Authorization": token if token.startswith("Bearer ") else f"Bearer {token}"},
            timeout=timeout,
            follow_redirects=True,
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()

    def get_my_items(self) -> list[AdvertisementDto]:
        url = f"{self._base_url}/{MY_ITEMS_URL.lstrip('/')}"
        logger.info("Fetching my items from Kufar API: %s", url)
        response = self._session.get(url)
        logger.info("Received response with status code: %d", response.status_code)
        response.raise_for_status()

        data = response.json()
        ads_raw = data.get("ads", [])

        logger.info("Found %d ads in the response.", len(ads_raw))
        parsed_items: list[AdvertisementDto] = []
        for ad in ads_raw:
            price_raw = ad.get("price_byn", "0")
            price = round(int(price_raw) / 100.0, 2) if str(price_raw).isdigit() else 0.0

            raw_date = ad.get("date") or ad.get("list_time") or ad.get("start_time")
            pub_date = datetime.fromisoformat(raw_date) if raw_date else datetime.now(tz=UTC)

            parsed_items.append(
                AdvertisementDto(
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

        sleep(uniform(1.5, 2.0))
        try:
            logger.info("Fetching item page HTML from Kufar: %s", item_url)
            response = self._session.get(item_url)
            logger.info("Received response with status code: %d", response.status_code)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning("Item page not found (404): %s", item_url)
                return ""
            if e.response.status_code == 429:
                logger.error(
                    "Kufar rate limit reached (HTTP 429) for %s. Backoff required.", item_url
                )
            else:
                logger.exception("HTTP status error while fetching item page HTML: %s", item_url)
            raise
        except httpx.RequestError:
            logger.exception("Network request error while fetching item page HTML: %s", item_url)
            raise
