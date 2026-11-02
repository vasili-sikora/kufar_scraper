import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import gspread
from gspread import Client, Spreadsheet, Worksheet

from config import GOOGLE_SERVICE_ACCOUNT_FILE, GOOGLE_SPREADSHEET_ID
from exporters.base import BaseExporter
from schemas import AdvertisementDto, AdvertisementHistoryDto

logger = logging.getLogger(__name__)


class GoogleSheetsExporter(BaseExporter[str]):
    """Экспортер данных в Google Таблицы через gspread."""

    def __init__(
        self,
        spreadsheet_id: str = GOOGLE_SPREADSHEET_ID,
        credentials_path: Path = GOOGLE_SERVICE_ACCOUNT_FILE,
        client: Client | None = None,
    ):
        self._spreadsheet_id = spreadsheet_id
        self._credentials_path = credentials_path
        self._client = client

    def _get_client(self) -> Client:
        if self._client is None:
            if not self._credentials_path.exists():
                raise FileNotFoundError(
                    f"Google credentials file not found at: {self._credentials_path}"
                )
            logger.info("Authorizing Google Service Account from %s", self._credentials_path)
            self._client = gspread.service_account(filename=str(self._credentials_path))
        return self._client

    def _get_or_create_worksheet(self, spreadsheet: Spreadsheet, title: str) -> Worksheet:
        try:
            return spreadsheet.worksheet(title)
        except gspread.WorksheetNotFound:
            logger.info("Worksheet '%s' not found. Creating a new one.", title)
            return spreadsheet.add_worksheet(title=title, rows=100, cols=20)

    def _populate_sheet(
        self,
        worksheet: Worksheet,
        headers: list[str],
        rows: list[list[Any]],
    ) -> None:
        worksheet.clear()

        updated_at = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
        worksheet.update(values=[[f"Последнее обновление: {updated_at}"]], range_name="A1")
        worksheet.format("A1", {"textFormat": {"italic": True, "bold": True}})

        data = [headers, *rows]
        worksheet.update(values=data, range_name="A3")

        end_col = chr(ord("A") + len(headers) - 1)
        worksheet.format(f"A3:{end_col}3", {"textFormat": {"bold": True}})

    def export(
        self,
        ads: list[AdvertisementDto],
        ads_history: list[AdvertisementHistoryDto] | None = None,
    ) -> str:
        if not ads:
            raise ValueError("Ads list is empty!")
        if not self._spreadsheet_id:
            raise ValueError("Google Spreadsheet ID is not specified!")

        client = self._get_client()
        logger.info("Opening Google Spreadsheet: %s", self._spreadsheet_id)
        spreadsheet = client.open_by_key(self._spreadsheet_id)

        ads_sheet = self._get_or_create_worksheet(spreadsheet, self.ADS_SHEET_TITLE)
        ads_rows = self._prepare_ads_rows(ads)
        self._populate_sheet(ads_sheet, self.ADS_HEADERS, ads_rows)
        logger.info("Updated %d ads in '%s'", len(ads_rows), self.ADS_SHEET_TITLE)

        if ads_history:
            history_sheet = self._get_or_create_worksheet(spreadsheet, self.HISTORY_SHEET_TITLE)
            history_rows = self._prepare_history_rows(ads_history)
            self._populate_sheet(history_sheet, self.HISTORY_HEADERS, history_rows)
            logger.info(
                "Updated %d history records in '%s'", len(history_rows), self.HISTORY_SHEET_TITLE
            )

        return spreadsheet.url
