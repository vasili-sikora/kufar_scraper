from pathlib import Path
from unittest.mock import MagicMock

import httpx
import pytest
from sqlalchemy.exc import SQLAlchemyError

from exceptions import KufarScraperError, KufarScraperNetworkError
from exporters import BaseExporter, ExcelExporter
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
    db_error = SQLAlchemyError("Database error")
    mock_repository.get_all.side_effect = db_error
    service = AdvertisementService(mock_repository)

    with pytest.raises(SQLAlchemyError) as exc_info:
        service.get_all_ads_from_db()

    assert exc_info.value is db_error


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
    assert saved_item.description == "Свежее описание"
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
    db_error = SQLAlchemyError("Database error")
    mock_repository.upsert.side_effect = db_error
    mock_client.get_my_items.return_value = [advertisement]
    mock_client.get_item_page_html.return_value = ""
    with pytest.raises(SQLAlchemyError) as exc_info:
        service_w_mock_repo.sync_ads_to_db(mock_client)

    assert exc_info.value is db_error


def test_export_ads_with_excel_exporter(
    service_w_mock_repo: AdvertisementService,
    mock_repository: MagicMock,
    advertisement: AdvertisementDto,
    tmp_path: Path,
):
    mock_repository.get_all.return_value = [advertisement]
    mock_repository.get_all_history.return_value = []
    test_filepath = tmp_path / "test.xlsx"

    result_path = service_w_mock_repo.export_ads(ExcelExporter(filepath=test_filepath))
    mock_repository.get_all.assert_called_once()
    mock_repository.get_all_history.assert_called_once()

    assert result_path.exists()


@pytest.mark.parametrize("repository_method", ["get_all", "get_all_history"])
def test_export_ads_throws_exception_on_db_error(
    service_w_mock_repo: AdvertisementService,
    mock_repository: MagicMock,
    repository_method: str,
):
    db_error = SQLAlchemyError("Database error")
    mock_repository.get_all.return_value = []
    getattr(mock_repository, repository_method).side_effect = db_error
    mock_exporter = MagicMock(spec=BaseExporter)

    with pytest.raises(SQLAlchemyError) as exc_info:
        service_w_mock_repo.export_ads(mock_exporter)

    assert exc_info.value is db_error


def test_get_advertisement_history_propagates_db_error(
    service_w_mock_repo: AdvertisementService, mock_repository: MagicMock
):
    db_error = SQLAlchemyError("Database error")
    mock_repository.get_history.side_effect = db_error

    with pytest.raises(SQLAlchemyError) as exc_info:
        service_w_mock_repo.get_advertisement_history(12345)

    assert exc_info.value is db_error


def test_export_ads_throws_exception_on_value_error(
    service_w_mock_repo: AdvertisementService, mock_repository: MagicMock
):
    mock_repository.get_all.return_value = []
    mock_repository.get_all_history.return_value = []
    mock_exporter = MagicMock(spec=BaseExporter)
    mock_exporter.export.side_effect = ValueError("Export failed")

    with pytest.raises(KufarScraperError):
        service_w_mock_repo.export_ads(mock_exporter)


def test_export_ads_throws_exception_on_os_error(
    service_w_mock_repo: AdvertisementService, mock_repository: MagicMock
):
    mock_repository.get_all.return_value = []
    mock_repository.get_all_history.return_value = []
    mock_exporter = MagicMock(spec=BaseExporter)
    mock_exporter.export.side_effect = OSError("Disk write failed")

    with pytest.raises(KufarScraperError):
        service_w_mock_repo.export_ads(mock_exporter)
