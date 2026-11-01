from pathlib import Path
from unittest.mock import MagicMock

import gspread
import pytest

from exporters import GoogleSheetsExporter
from schemas import AdvertisementDto, AdvertisementHistoryDto


def test_google_sheets_exporter_raises_value_error_on_empty_ads():
    exporter = GoogleSheetsExporter(spreadsheet_id="test_id")
    with pytest.raises(ValueError, match="Ads list is empty"):
        exporter.export([])


def test_google_sheets_exporter_raises_value_error_on_empty_spreadsheet_id(
    advertisement: AdvertisementDto,
):
    exporter = GoogleSheetsExporter(spreadsheet_id="")
    with pytest.raises(ValueError, match="Google Spreadsheet ID is not specified"):
        exporter.export([advertisement])


def test_google_sheets_exporter_raises_file_not_found_on_missing_credentials(
    advertisement: AdvertisementDto, tmp_path: Path
):
    missing_creds = tmp_path / "non_existent.json"
    exporter = GoogleSheetsExporter(spreadsheet_id="some_id", credentials_path=missing_creds)
    with pytest.raises(FileNotFoundError, match="Google credentials file not found"):
        exporter.export([advertisement])


def test_google_sheets_exporter_successful_export_with_history(
    advertisement: AdvertisementDto,
    adv_history: AdvertisementHistoryDto,
):
    mock_client = MagicMock(spec=gspread.Client)
    mock_spreadsheet = MagicMock(spec=gspread.Spreadsheet)
    mock_spreadsheet.url = "https://docs.google.com/spreadsheets/d/test_id"

    mock_ads_sheet = MagicMock(spec=gspread.Worksheet)
    mock_history_sheet = MagicMock(spec=gspread.Worksheet)

    def worksheet_side_effect(title):
        if title == "Объявления":
            return mock_ads_sheet
        if title == "История изменений":
            return mock_history_sheet
        raise gspread.WorksheetNotFound()

    mock_spreadsheet.worksheet.side_effect = worksheet_side_effect
    mock_client.open_by_key.return_value = mock_spreadsheet

    exporter = GoogleSheetsExporter(
        spreadsheet_id="test_id",
        client=mock_client,
    )

    url = exporter.export(ads=[advertisement], ads_history=[adv_history])

    assert url == "https://docs.google.com/spreadsheets/d/test_id"
    mock_client.open_by_key.assert_called_once_with("test_id")

    # Проверяем заполнение листа объявлений
    mock_ads_sheet.clear.assert_called_once()
    mock_ads_sheet.update.assert_called_once()
    mock_ads_sheet.format.assert_called_once()

    # Проверяем заполнение листа истории
    mock_history_sheet.clear.assert_called_once()
    mock_history_sheet.update.assert_called_once()
    mock_history_sheet.format.assert_called_once()


def test_google_sheets_exporter_creates_sheet_if_not_found(
    advertisement: AdvertisementDto,
):
    mock_client = MagicMock(spec=gspread.Client)
    mock_spreadsheet = MagicMock(spec=gspread.Spreadsheet)
    mock_spreadsheet.url = "https://docs.google.com/spreadsheets/d/test_id"

    # При поиске листа выбрасываем WorksheetNotFound
    mock_spreadsheet.worksheet.side_effect = gspread.WorksheetNotFound()
    created_sheet = MagicMock(spec=gspread.Worksheet)
    mock_spreadsheet.add_worksheet.return_value = created_sheet
    mock_client.open_by_key.return_value = mock_spreadsheet

    exporter = GoogleSheetsExporter(
        spreadsheet_id="test_id",
        client=mock_client,
    )

    url = exporter.export(ads=[advertisement])

    assert url == "https://docs.google.com/spreadsheets/d/test_id"
    mock_spreadsheet.add_worksheet.assert_called_once_with(title="Объявления", rows=100, cols=20)
    created_sheet.clear.assert_called_once()
    created_sheet.update.assert_called_once()
