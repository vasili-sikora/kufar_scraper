from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from config import DATA_DIR
from schemas import AdvertisementItem

EXCEL_PATH = DATA_DIR / "advertisements.xlsx"


def export_to_excel(ads: list[AdvertisementItem], filepath: Path = EXCEL_PATH) -> Path:
    filepath.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise ValueError("Не удалось получить текущий лист")
    ws.title = "Объявления"

    headers = [
        "Kufar ID",
        "Название",
        "Цена",
        "Статус",
        "Описание",
        "Дата публикации",
        "Ссылка",
    ]
    ws.append(headers)

    header_font = Font(bold=True)
    header_alignment = Alignment(horizontal="center", vertical="center")
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = header_alignment

    for ad in ads:
        pub_date = ad.published_at.strftime("%Y-%m-%d %H:%M") if ad.published_at else ""
        ws.append(
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

    column_widths = {
        "A": 14,  # Kufar ID
        "B": 35,  # Название
        "C": 12,  # Цена
        "D": 12,  # Статус
        "E": 50,  # Описание
        "F": 18,  # Дата публикации
        "G": 35,  # Ссылка
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    wb.save(filepath)
    return filepath
