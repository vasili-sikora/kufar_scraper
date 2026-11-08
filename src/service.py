import logging

import httpx

from exceptions import KufarScraperError, KufarScraperNetworkError
from exporters import BaseExporter
from parser import AdvertisementHtmlParser
from repository import AdvertisementRepository
from schemas import AdvertisementDto, AdvertisementHistoryDto

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
            raise KufarScraperNetworkError("Failed to fetch advertisements") from e

    def get_all_ads_from_db(self) -> list[AdvertisementDto]:
        logger.info("Fetching all ads from database...")
        ads = self._repository.get_all()
        logger.info(f"Fetched {len(ads)} ads from database.")
        return [AdvertisementDto.from_orm(ad) for ad in ads]

    def export_ads[T](self, exporter: BaseExporter[T]) -> T:
        try:
            logger.info("Exporting ads...")
            ads = self.get_all_ads_from_db()
            ads_history_orm = self._repository.get_all_history()
            ads_history = [AdvertisementHistoryDto.from_orm(a) for a in ads_history_orm]
            result = exporter.export(ads=ads, ads_history=ads_history)
            logger.info("Ads exported successfully.")
            return result
        except (ValueError, OSError) as e:
            logger.exception("Error while exporting ads")
            raise KufarScraperError("Failed to export data") from e

    def get_advertisement_history(self, advertisement_id: int) -> list[AdvertisementHistoryDto]:
        logger.info(f"Fetching advertisement history for ID: {advertisement_id}")
        ads = self._repository.get_history(advertisement_id)
        logger.info(f"Fetched {len(ads)} history records for advertisement ID: {advertisement_id}")
        return [AdvertisementHistoryDto.from_orm(ad) for ad in ads]
