import logging
from pathlib import Path

import httpx

from config import DATA_DIR
from exceptions import KufarScraperError, KufarScraperNetworkError
from exporter import export_to_excel
from parser import AdvertisementHtmlParser
from repository import AdvertisementRepository
from schemas import AdvertisementDto, AdvertisementHistoryDto

EXCEL_PATH = DATA_DIR / "advertisements.xlsx"

logger = logging.getLogger(__name__)


class AdvertisementService:
    def __init__(self, repository: AdvertisementRepository):
        self._repository = repository

    def sync_ads_to_db(self, client) -> None:
        try:
            logger.info("Syncing ads to database...")
            ads = client.get_my_items()
            logger.info(f"Found {len(ads)} ads to sync.")

            for ad in ads:
                if ad.link:
                    ad_html = client.get_item_page_html(ad.link)
                    ad.description = AdvertisementHtmlParser(ad_html).get_item_description()
                self._repository.upsert(ad)
            logger.info(f"Processed {len(ads)} ads.")
        except httpx.HTTPError as e:
            logger.exception("Network error while syncing ads")
            raise KufarScraperNetworkError("Не удалось загрузить объявления") from e

    def get_all_ads_from_db(self) -> list[AdvertisementDto]:
        logger.info("Fetching all ads from database...")
        ads = self._repository.get_all()
        logger.info(f"Fetched {len(ads)} ads from database.")
        return [AdvertisementDto.from_orm(ad) for ad in ads]

    def save_to_excel(self, filepath: Path = EXCEL_PATH) -> Path:
        try:
            logger.info("Saving ads to Excel...")
            ads = self.get_all_ads_from_db()
            ads_history_orm = self._repository.get_all_history()
            ads_history = [AdvertisementHistoryDto.from_orm(a) for a in ads_history_orm]
            excel_path = export_to_excel(
                ads=ads,
                ads_history=ads_history,
                filepath=filepath,
            )
            logger.info(f"Ads saved to Excel at {excel_path}")
            return excel_path
        except (ValueError, OSError) as e:
            logger.exception("Error while saving ads to Excel")
            raise KufarScraperError("Не удалось создать отчёт в Excel") from e

    def get_advertisement_history(self, advertisement_id: int) -> list[AdvertisementHistoryDto]:
        logger.info(f"Fetching advertisement history for ID: {advertisement_id}")
        ads = self._repository.get_history(advertisement_id)
        logger.info(f"Fetched {len(ads)} history records for advertisement ID: {advertisement_id}")
        return [AdvertisementHistoryDto.from_orm(ad) for ad in ads]
