from abc import ABC, abstractmethod
from typing import Any, ClassVar

from schemas import AdvertisementDto, AdvertisementHistoryDto


class BaseExporter[T](ABC):
    """Base abstract exporter class."""

    ADS_SHEET_TITLE: ClassVar[str] = "Advertisements"
    HISTORY_SHEET_TITLE: ClassVar[str] = "Change History"

    ADS_HEADERS: ClassVar[list[str]] = [
        "Kufar ID",
        "Title",
        "Price",
        "Status",
        "Description",
        "Publication Date",
        "Link",
    ]

    HISTORY_HEADERS: ClassVar[list[str]] = [
        "Ad ID",
        "Field",
        "Old Value",
        "New Value",
        "Change Date",
    ]

    def _prepare_ads_rows(self, ads: list[AdvertisementDto]) -> list[list[Any]]:
        rows: list[list[Any]] = []
        for ad in ads:
            pub_date = ad.published_at.strftime("%Y-%m-%d %H:%M") if ad.published_at else ""
            rows.append(
                [
                    ad.kufar_id,
                    ad.title,
                    ad.price,
                    ad.status,
                    ad.description or "",
                    pub_date,
                    ad.link,
                ]
            )
        return rows

    def _prepare_history_rows(self, ads_history: list[AdvertisementHistoryDto]) -> list[list[Any]]:
        rows: list[list[Any]] = []
        for record in ads_history:
            change_date = record.changed_at.strftime("%Y-%m-%d %H:%M") if record.changed_at else ""
            rows.append(
                [
                    record.kufar_id,
                    record.field_name,
                    record.old_value or "",
                    record.new_value,
                    change_date,
                ]
            )
        return rows

    @abstractmethod
    def export(
        self,
        ads: list[AdvertisementDto],
        ads_history: list[AdvertisementHistoryDto] | None = None,
    ) -> T:
        """Export advertisements and change history data."""
