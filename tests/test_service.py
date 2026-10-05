from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from sqlalchemy.exc import SQLAlchemyError

from exceptions import KufarScraperDatabaseError, KufarScraperError, KufarScraperNetworkError
from schemas import AdvertisementDto
from service import AdvertisementService


def test_get_all_ads_return_empty_list_when_no_ads(service: AdvertisementService):
    ads = service.get_all_ads_from_db()
    assert ads == []


def test_get_all_return_non_empty_list(
    mock_repository: MagicMock,
    service_w_mock_repo: AdvertisementService,
    advertisement: AdvertisementDto,
):
    mock_repository.get_all.return_value = [advertisement]
    ads = service_w_mock_repo.get_all_ads_from_db()
    assert len(ads) == 1
    assert ads[0].kufar_id == advertisement.kufar_id
    assert ads[0].title == advertisement.title
    assert ads[0].price == advertisement.price
    assert ads[0].description == advertisement.description


def test_get_all_throws_exception_on_db_error(mock_repository: MagicMock):
    mock_repository.get_all.side_effect = SQLAlchemyError("Database error")
    service = AdvertisementService(mock_repository)

    with pytest.raises(KufarScraperError):
        service.get_all_ads_from_db()


def test_sync_ads_to_db_success(
    service_w_mock_repo: AdvertisementService,
    mock_repository: MagicMock,
    advertisement: AdvertisementDto,
    mock_client: MagicMock,
):
    mock_client.get_my_items.return_value = [advertisement]
    mock_client.get_item_page_html.return_value = """
            <script id="__NEXT_DATA__" type="application/json">
            {"props": {"initialState": {"adView": {"data": {"body": "Свежее описание"}}}}}
            </script>
        """

    service_w_mock_repo.sync_ads_to_db(mock_client)

    mock_client.get_my_items.assert_called_once()
    mock_client.get_item_page_html.assert_called_once_with(advertisement.link)

    mock_repository.upsert.assert_called_once()
    saved_item = mock_repository.upsert.call_args[0][0]
    assert saved_item.description == advertisement.description
    assert saved_item.kufar_id == advertisement.kufar_id


def test_sync_ads_to_db_throws_exc_on_http_error(
    service_w_mock_repo: AdvertisementService,
    mock_client: MagicMock,
):
    mock_client.get_my_items.side_effect = httpx.HTTPError("Network Error")

    with pytest.raises(KufarScraperNetworkError):
        service_w_mock_repo.sync_ads_to_db(mock_client)


def test_sync_ads_to_db_throws_exception_on_db_error(
    service_w_mock_repo: AdvertisementService,
    mock_repository: MagicMock,
    mock_client: MagicMock,
    advertisement: AdvertisementDto,
):
    mock_repository.upsert.side_effect = SQLAlchemyError("Database error")
    mock_client.get_my_items.return_value = [advertisement]
    mock_client.get_item_page_html.return_value = ""
    with pytest.raises(KufarScraperDatabaseError):
        service_w_mock_repo.sync_ads_to_db(mock_client)


def test_save_to_excel(
    service_w_mock_repo: AdvertisementService,
    mock_repository: MagicMock,
    advertisement: AdvertisementDto,
    tmp_path: Path,
):
    mock_repository.get_all.return_value = [advertisement]
    test_filepath = tmp_path / "test.xlsx"
    service_w_mock_repo.save_to_excel(filepath=test_filepath)
    mock_repository.get_all.assert_called_once()

    assert test_filepath.exists()


# TODO: Make this unit tests instead of integration with excel exporter mock
def test_save_to_excel_throws_exception_on_db_error(
    service_w_mock_repo: AdvertisementService, mock_repository: MagicMock, tmp_path: Path
):
    mock_repository.get_all.side_effect = SQLAlchemyError("Database error")
    with pytest.raises(KufarScraperDatabaseError):
        service_w_mock_repo.save_to_excel(filepath=tmp_path / "test.xlsx")


def test_save_to_excel_throws_exception_on_value_error(
    service_w_mock_repo: AdvertisementService, mock_repository: MagicMock, tmp_path: Path
):
    with (
        patch("service.export_to_excel", side_effect=ValueError()),
        pytest.raises(KufarScraperError),
    ):
        service_w_mock_repo.save_to_excel(filepath=tmp_path / "test.xlsx")


def test_save_to_excel_throws_exception_on_os_error(
    service_w_mock_repo: AdvertisementService, mock_repository: MagicMock, tmp_path: Path
):
    with (
        patch("service.export_to_excel", side_effect=OSError()),
        pytest.raises(KufarScraperError),
    ):
        service_w_mock_repo.save_to_excel(filepath=tmp_path / "test.xlsx")
