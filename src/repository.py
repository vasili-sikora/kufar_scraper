from sqlalchemy import select
from sqlalchemy.orm import Session

from models import AdvertisementHistoryOrm, AdvertisementOrm
from schemas import AdvertisementDto


class AdvertisementRepository:
    def __init__(self, session: Session):
        self._session: Session = session

    def get_by_kufar_id(self, kufar_id: int) -> AdvertisementOrm | None:
        return self._session.get(AdvertisementOrm, kufar_id)

    def upsert(self, item: AdvertisementDto) -> AdvertisementOrm:
        ad_orm = self.get_by_kufar_id(item.kufar_id)

        if ad_orm is None:
            ad_orm = AdvertisementOrm(
                kufar_id=item.kufar_id,
                title=item.title,
                description=item.description,
                price=item.price,
                status=item.status,
                link=item.link,
                published_at=item.published_at,
            )
            self._session.add(ad_orm)
        else:
            if item.title != ad_orm.title:
                self._add_history_snapshot(old=ad_orm, new=item, field_name="title")
                ad_orm.title = item.title
            if item.price != ad_orm.price:
                self._add_history_snapshot(old=ad_orm, new=item, field_name="price")
                ad_orm.price = item.price
            if item.status != ad_orm.status:
                self._add_history_snapshot(old=ad_orm, new=item, field_name="status")
                ad_orm.status = item.status
            ad_orm.link = item.link

            if item.description and ad_orm.description != item.description:
                self._add_history_snapshot(old=ad_orm, new=item, field_name="description")
                ad_orm.description = item.description

        return ad_orm

    def get_all(self) -> list[AdvertisementOrm]:
        query = select(AdvertisementOrm).order_by(AdvertisementOrm.published_at.desc())
        return list(self._session.scalars(query).all())

    def _add_history_snapshot(
        self, old: AdvertisementOrm, new: AdvertisementDto, field_name: str
    ) -> None:
        history_orm = AdvertisementHistoryOrm(
            kufar_id=old.kufar_id,
            field_name=field_name,
            old_value=getattr(old, field_name),
            new_value=getattr(new, field_name),
        )
        self._session.add(history_orm)

    def get_history(self, kufar_id: int) -> list[AdvertisementHistoryOrm]:
        query = (
            select(AdvertisementHistoryOrm)
            .where(AdvertisementHistoryOrm.kufar_id == kufar_id)
            .order_by(AdvertisementHistoryOrm.changed_at.desc())
        )
        return list(self._session.scalars(query).all())
