from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from client import KufarClient
from models import Base
from repository import AdvertisementRepository
from schemas import AdvertisementDto, AdvertisementHistoryDto
from service import AdvertisementService


@pytest.fixture
def db_session() -> Generator[Session]:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(engine)
    with session_factory() as session:
        yield session


@pytest.fixture
def repository(db_session: Session) -> AdvertisementRepository:
    return AdvertisementRepository(db_session)


@pytest.fixture
def client() -> Generator[KufarClient]:
    with KufarClient() as client:
        yield client


@pytest.fixture
def service(repository: AdvertisementRepository) -> AdvertisementService:
    return AdvertisementService(repository)


@pytest.fixture
def advertisement() -> AdvertisementDto:
    item = AdvertisementDto(
        kufar_id=12345,
        title="Компьютер супер крутой лютый",
        price=1500.0,
        status="active",
        link="http://kufar.by/item/12345",
        published_at=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        description="8 ядер, 16 ГБ ОЗУ",
    )
    return item


@pytest.fixture
def mock_repository() -> MagicMock:
    mock_repository = MagicMock(spec=AdvertisementRepository)
    return mock_repository


@pytest.fixture
def mock_client() -> MagicMock:
    mock_client = MagicMock(spec=KufarClient)
    return mock_client


@pytest.fixture
def mock_service() -> MagicMock:
    mock_service = MagicMock(spec=AdvertisementService)
    return mock_service


@pytest.fixture
def service_w_mock_repo(mock_repository: MagicMock) -> AdvertisementService:
    service = AdvertisementService(mock_repository)
    return service


@pytest.fixture
def adv_history(advertisement: AdvertisementDto) -> AdvertisementHistoryDto:
    adv_history = AdvertisementHistoryDto(
        id=1,
        kufar_id=advertisement.kufar_id,
        field_name="title",
        old_value="old",
        new_value="new",
        changed_at=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
    )
    return adv_history
