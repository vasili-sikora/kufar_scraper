from pathlib import Path

import httpx
from sqlalchemy.exc import SQLAlchemyError

from config import DATA_DIR
from exceptions import KufarApiError, KufarScrapperException
from exporter import export_to_excel
from logger import log
from parser import ItemHtmlParser
from schemas import AdvertisementItem

EXCEL_PATH = DATA_DIR / "advertisements.xlsx"


class KufarService:
    def __init__(self, repository):
        self._repository = repository

    @log
    def sync_ads_to_db(self, client) -> None:
        try:
            ads = client.get_my_items()

            for ad in ads:
                if ad.link:
                    ad_html = client.get_item_page_html(ad.link)
                    ad.description = ItemHtmlParser(ad_html).get_item_description()
                self._repository.upsert(ad)
        except httpx.HTTPError as e:
            raise KufarApiError("Не удалось загрузить объявления") from e

    @log
    def get_all_ads_from_db(self) -> list[AdvertisementItem]:
        try:
            ads = self._repository.get_all()
            return [AdvertisementItem.from_orm(ad) for ad in ads]
        except SQLAlchemyError as e:
            raise KufarScrapperException("Не удалось получить объявления из базы") from e

    @log
    def save_to_excel(self, client) -> Path:
        try:
            self.sync_ads_to_db(client)
            ads = self.get_all_ads_from_db()
            excel_path = export_to_excel(ads, EXCEL_PATH)
            return excel_path
        except (ValueError, OSError) as e:
            raise KufarScrapperException("Не удалось создать отчёт в Excel") from e
