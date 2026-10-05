from pathlib import Path

import pytest

from exporter import export_to_excel
from schemas import AdvertisementDto


def test_save_to_excel_throws_value_error_on_empty_ads_list(tmp_path: Path):
    ads = []
    with pytest.raises(ValueError):
        export_to_excel(ads, tmp_path / "test.xlsx")


def test_save_to_excel_throws_value_error_on_empty_path(item: AdvertisementDto):
    with pytest.raises(ValueError):
        export_to_excel([item], Path(""))


def test_save_to_excel_success(item: AdvertisementDto, tmp_path: Path):
    export_to_excel([item], tmp_path / "test.xlsx")
    assert (tmp_path / "test.xlsx").exists()
