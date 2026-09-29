from sqlalchemy import select
from sqlalchemy.orm import Session

from models import AdvertisementOrm
from schemas import AdvertisementItem


class AdvertisementRepository:
    def __init__(self, session: Session):
        self._session: Session = session

    def get_by_kufar_id(self, kufar_id: int) -> AdvertisementOrm | None:
        query = select(AdvertisementOrm).where(AdvertisementOrm.kufar_id == kufar_id)
        return self._session.scalars(query).one_or_none()

    def upsert(self, item: AdvertisementItem) -> AdvertisementOrm:
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
            ad_orm.title = item.title
            ad_orm.price = item.price
            ad_orm.status = item.status
            ad_orm.link = item.link

            if item.description:
                ad_orm.description = item.description

        return ad_orm

    def get_all(self) -> list[AdvertisementOrm]:
        query = select(AdvertisementOrm).order_by(AdvertisementOrm.published_at.desc())
        return list(self._session.scalars(query).all())
