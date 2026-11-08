from pathlib import Path

import pytest
from openpyxl import load_workbook

from exporters import ExcelExporter, export_to_excel
from schemas import AdvertisementDto, AdvertisementHistoryDto


def test_excel_exporter_throws_value_error_on_empty_ads_list(tmp_path: Path):
    ads = []
    with pytest.raises(ValueError):
        export_to_excel(ads, filepath=(tmp_path / "test.xlsx"))


def test_excel_exporter_creates_file_with_correct_sheets(
    tmp_path: Path,
    advertisement: AdvertisementDto,
    adv_history: AdvertisementHistoryDto,
):
    ads = [advertisement]
    history = [adv_history]
    file_path = tmp_path / "test.xlsx"

    exporter = ExcelExporter(filepath=file_path)
    result_path = exporter.export(ads, history)

    assert result_path.exists()
    wb = load_workbook(result_path)
    assert ExcelExporter.ADS_SHEET_TITLE in wb.sheetnames
    assert ExcelExporter.HISTORY_SHEET_TITLE in wb.sheetnames


def test_excel_exporter_without_history(tmp_path: Path, advertisement: AdvertisementDto):
    ads = [advertisement]
    file_path = tmp_path / "test.xlsx"

    exporter = ExcelExporter(filepath=file_path)
    result_path = exporter.export(ads)

    assert result_path.exists()
    wb = load_workbook(result_path)
    assert ExcelExporter.ADS_SHEET_TITLE in wb.sheetnames
    assert ExcelExporter.HISTORY_SHEET_TITLE not in wb.sheetnames
