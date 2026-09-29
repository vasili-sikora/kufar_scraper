from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models import Base
from repository import AdvertisementRepository
from schemas import AdvertisementItem


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    session_factory = sessionmaker(engine)
    session = session_factory()

    yield session

    session.close()


@pytest.fixture
def repository(db_session: Session):
    return AdvertisementRepository(db_session)


def test_upsert_creates_new_ad(
    repository: AdvertisementRepository, db_session: Session
):
    item = AdvertisementItem(
        kufar_id=12345,
        title="Компьютер супер крутой лютый",
        price=1500.0,
        status="active",
        link="http://kufar.by/item/12345",
        published_at=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        description="8 ядер, 16 ГБ ОЗУ",
    )

    _ = repository.upsert(item)
    db_session.commit()

    saved = repository.get_by_kufar_id(12345)

    assert saved is not None
    assert saved.kufar_id == item.kufar_id
    assert saved.title == item.title
    assert saved.price == item.price
    assert saved.description == item.description


def test_upsert_updates_existing(
    repository: AdvertisementRepository, db_session: Session
):
    item = AdvertisementItem(
        kufar_id=12345,
        title="Компьютер супер крутой лютый",
        price=1500.0,
        status="active",
        link="http://kufar.by/item/12345",
        published_at=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        description="8 ядер, 16 ГБ ОЗУ",
    )

    _ = repository.upsert(item)
    db_session.commit()

    item.price = 1600.0
    _ = repository.upsert(item)

    updated = repository.get_by_kufar_id(item.kufar_id)

    assert updated is not None
    assert updated.kufar_id == item.kufar_id
    assert updated.price == 1600.0
    assert len(repository.get_all()) == 1


def test_description_not_deleted_on_status_change(
    repository: AdvertisementRepository, db_session: Session
):
    item = AdvertisementItem(
        kufar_id=12345,
        title="Компьютер супер крутой лютый",
        price=1500.0,
        status="active",
        link="http://kufar.by/item/12345",
        published_at=datetime(2026, 9, 1, 12, 0, tzinfo=UTC),
        description="8 ядер, 16 ГБ ОЗУ",
    )

    _ = repository.upsert(item)
    db_session.commit()

    item.description = None
    item.status = "sold"

    _ = repository.upsert(item)

    updated = repository.get_by_kufar_id(12345)
    assert updated is not None
    assert updated.description == "8 ядер, 16 ГБ ОЗУ"
