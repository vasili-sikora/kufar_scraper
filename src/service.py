from pathlib import Path

import httpx
from sqlalchemy.exc import SQLAlchemyError

from config import DATA_DIR
from exceptions import KufarScraperDatabaseError, KufarScraperError, KufarScraperNetworkError
from exporter import export_to_excel
from logger import log
from parser import AdvertisementHtmlParser
from repository import AdvertisementRepository
from schemas import AdvertisementDto, AdvertisementHistoryDto

EXCEL_PATH = DATA_DIR / "advertisements.xlsx"


class AdvertisementService:
    def __init__(self, repository: AdvertisementRepository):
        self._repository = repository

    @log
    def sync_ads_to_db(self, client) -> None:
        try:
            ads = client.get_my_items()

            for ad in ads:
                if ad.link:
                    ad_html = client.get_item_page_html(ad.link)
                    ad.description = AdvertisementHtmlParser(ad_html).get_item_description()
                self._repository.upsert(ad)
        except httpx.HTTPError as e:
            raise KufarScraperNetworkError("Не удалось загрузить объявления") from e
        except SQLAlchemyError as e:
            raise KufarScraperDatabaseError() from e

    @log
    def get_all_ads_from_db(self) -> list[AdvertisementDto]:
        try:
            ads = self._repository.get_all()
            return [AdvertisementDto.from_orm(ad) for ad in ads]
        except SQLAlchemyError as e:
            raise KufarScraperDatabaseError("Не удалось получить объявления из базы") from e

    @log
    def save_to_excel(self, filepath: Path = EXCEL_PATH) -> Path:
        try:
            ads = self.get_all_ads_from_db()
            ads_history_orm = self._repository.get_all_history()
            ads_history = [AdvertisementHistoryDto.from_orm(a) for a in ads_history_orm]
            excel_path = export_to_excel(
                ads=ads,
                ads_history=ads_history,
                filepath=filepath,
            )
            return excel_path
        except SQLAlchemyError as e:
            raise KufarScraperDatabaseError() from e
        except (ValueError, OSError) as e:
            raise KufarScraperError("Не удалось создать отчёт в Excel") from e

    @log
    def get_advertisement_history(self, advertisement_id: int) -> list[AdvertisementHistoryDto]:
        try:
            ads = self._repository.get_history(advertisement_id)
            return [AdvertisementHistoryDto.from_orm(ad) for ad in ads]
        except SQLAlchemyError as e:
            raise KufarScraperDatabaseError() from e
