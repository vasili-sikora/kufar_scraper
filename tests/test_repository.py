import copy
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from repository import AdvertisementRepository
from schemas import AdvertisementDto


def test_upsert_creates_new_ad(repository: AdvertisementRepository, db_session: Session):
    item = AdvertisementDto(
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


def test_upsert_updates_existing(repository: AdvertisementRepository, db_session: Session):
    item = AdvertisementDto(
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
    item = AdvertisementDto(
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


def test_new_ad_not_create_history(repository: AdvertisementRepository, item: AdvertisementDto):
    _ = repository.upsert(item)

    assert repository.get_history(item.kufar_id) == []
    assert repository.get_by_kufar_id(item.kufar_id) is not None


def test_updating_ad_create_history(repository: AdvertisementRepository, item: AdvertisementDto):
    _ = repository.upsert(item)

    updated_item = copy.copy(item)
    updated_item.title = "new_title"

    _ = repository.upsert(updated_item)

    history = repository.get_history(item.kufar_id)
    assert len(history) == 1
    assert history[0].kufar_id == item.kufar_id
    assert history[0].field_name == "title"
    assert history[0].old_value == item.title
    assert history[0].new_value == "new_title"


def test_upsert_not_create_history_if_nothing_changed(
    repository: AdvertisementRepository, item: AdvertisementDto
):
    _ = repository.upsert(item)
    _ = repository.upsert(item)

    history = repository.get_history(item.kufar_id)
    assert history == []
