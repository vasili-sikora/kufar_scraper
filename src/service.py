import httpx

from client import KufarClient
from db import SessionFactory
from exceptions import KufarApiError
from parser import ItemHtmlParser


class KufarService:
    def __init__(self, client, repository):
        self._client = client
        self._repository = repository

    def sync_ads_to_db(self) -> None:
        with SessionFactory() as session, self._client as client:
            try:
                ads = client.get_my_items()
                for ad in ads:
                    if ad.link:
                        ad_html = self._client.get_item_page_html(ad.link)
                        ad.description = ItemHtmlParser(ad_html).get_item_description()
                    self._repository.upsert(ad)
                self._repository._session.commit()
            except httpx.HTTPError:
                raise KufarApiError()
