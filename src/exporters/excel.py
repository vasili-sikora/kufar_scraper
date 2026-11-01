from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from config import DATA_DIR
from exporters.base import BaseExporter
from schemas import AdvertisementDto, AdvertisementHistoryDto

EXCEL_PATH = DATA_DIR / "advertisements.xlsx"
HEADER_FONT = Font(bold=True)
HEADER_ALIGNMENT = Alignment(horizontal="center", vertical="center")

ADS_COLUMN_WIDTHS = {
    "A": 14,  # Kufar ID
    "B": 35,  # Название
    "C": 12,  # Цена
    "D": 12,  # Статус
    "E": 50,  # Описание
    "F": 18,  # Дата публикации
    "G": 35,  # Ссылка
}

HISTORY_COLUMN_WIDTHS = {
    "A": 16,  # ID объявления
    "B": 16,  # Поле
    "C": 30,  # Старое значение
    "D": 30,  # Новое значение
    "E": 20,  # Дата изменения
}


class ExcelExporter(BaseExporter[Path]):
    def __init__(self, filepath: Path = EXCEL_PATH):
        self.filepath = filepath

    def _export_ads_history(self, wb: Workbook, ads_history: list[AdvertisementHistoryDto]) -> None:
        if not ads_history:
            return
        ws = wb.create_sheet(title=self.HISTORY_SHEET_TITLE)
        ws.append(self.HISTORY_HEADERS)

        for cell in ws[1]:
            cell.font = HEADER_FONT
            cell.alignment = HEADER_ALIGNMENT

        for row in self._prepare_history_rows(ads_history):
            ws.append(row)

        for col, width in HISTORY_COLUMN_WIDTHS.items():
            ws.column_dimensions[col].width = width

    def _export_ads(self, wb: Workbook, ads: list[AdvertisementDto]) -> None:
        ws = wb.active
        if ws is None:
            raise ValueError("Something went wrong!")

        ws.title = self.ADS_SHEET_TITLE
        ws.append(self.ADS_HEADERS)

        for cell in ws[1]:
            cell.font = HEADER_FONT
            cell.alignment = HEADER_ALIGNMENT

        for row in self._prepare_ads_rows(ads):
            ws.append(row)

        for col_letter, width in ADS_COLUMN_WIDTHS.items():
            ws.column_dimensions[col_letter].width = width

    def export(
        self,
        ads: list[AdvertisementDto],
        ads_history: list[AdvertisementHistoryDto] | None = None,
    ) -> Path:
        if not ads:
            raise ValueError("Ads list is empty!")
        if not self.filepath or not self.filepath.name:
            raise ValueError("Invalid filepath!")
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

        wb = Workbook()
        self._export_ads(wb, ads)
        if ads_history:
            self._export_ads_history(wb, ads_history)

        wb.save(self.filepath)
        return self.filepath


def export_to_excel(
    ads: list[AdvertisementDto],
    ads_history: list[AdvertisementHistoryDto] | None = None,
    filepath: Path = EXCEL_PATH,
) -> Path:
    """Функция-обёртка для обратной совместимости."""
    exporter = ExcelExporter(filepath=filepath)
    return exporter.export(ads=ads, ads_history=ads_history)
