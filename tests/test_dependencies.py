from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

import dependencies
from dependencies import get_service
from exceptions import KufarScraperDatabaseError, KufarScraperNetworkError
from models import AdvertisementOrm
from schemas import AdvertisementDto


@pytest.fixture
def isolated_session_factory(db_session: Session, monkeypatch: pytest.MonkeyPatch):
    factory = sessionmaker(bind=db_session.get_bind())
    monkeypatch.setattr(dependencies, "session_factory", factory)
    return factory


def test_get_service_commits_changes(
    isolated_session_factory,
    advertisement: AdvertisementDto,
    mock_client: MagicMock,
):
    mock_client.get_my_items.return_value = [advertisement]
    mock_client.get_item_page_html.return_value = ""

    with get_service() as service:
        service.sync_ads_to_db(mock_client)

    with isolated_session_factory() as session:
        saved = session.get(AdvertisementOrm, advertisement.kufar_id)
        assert saved is not None
        assert saved.title == advertisement.title


def test_get_service_translates_db_error_and_rolls_back(
    isolated_session_factory,
    advertisement: AdvertisementDto,
    mock_client: MagicMock,
):
    mock_client.get_my_items.return_value = [advertisement]
    mock_client.get_item_page_html.return_value = ""
    db_error = SQLAlchemyError("Database error")

    with pytest.raises(KufarScraperDatabaseError) as exc_info, get_service() as service:
        service.sync_ads_to_db(mock_client)
        # The query flushes the pending INSERT before the failure.
        assert len(service.get_all_ads_from_db()) == 1
        raise db_error

    assert exc_info.value.__cause__ is db_error
    with isolated_session_factory() as session:
        assert session.get(AdvertisementOrm, advertisement.kufar_id) is None


def test_get_service_preserves_application_error_and_rolls_back(
    isolated_session_factory,
    advertisement: AdvertisementDto,
    mock_client: MagicMock,
):
    mock_client.get_my_items.return_value = [advertisement]
    mock_client.get_item_page_html.return_value = ""
    network_error = KufarScraperNetworkError("Network error")

    with pytest.raises(KufarScraperNetworkError) as exc_info, get_service() as service:
        service.sync_ads_to_db(mock_client)
        assert len(service.get_all_ads_from_db()) == 1
        raise network_error

    assert exc_info.value is network_error
    with isolated_session_factory() as session:
        assert session.get(AdvertisementOrm, advertisement.kufar_id) is None


@pytest.mark.parametrize("failure_stage", ["__enter__", "__exit__"])
def test_get_service_translates_session_lifecycle_error(
    monkeypatch: pytest.MonkeyPatch, failure_stage: str
):
    factory = MagicMock()
    db_error = SQLAlchemyError("Session lifecycle error")
    transaction = factory.begin.return_value
    getattr(transaction, failure_stage).side_effect = db_error
    monkeypatch.setattr(dependencies, "session_factory", factory)

    with pytest.raises(KufarScraperDatabaseError) as exc_info, get_service():
        pass

    assert exc_info.value.__cause__ is db_error
