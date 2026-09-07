from sqlalchemy.sql.expression import select

from kufar_scraper.kufar.dto import Advertisement
from kufar_scraper.sqlite.models import AdvertisementORM


class AdvertisementSQLiteRepository:
    def __init__(self, sessionmaker):
        self.sessionmaker = sessionmaker

    def add_advertisement(self, advertisement: Advertisement) -> None:
        with self.sessionmaker as session:
            try:
                advertisement_orm = AdvertisementORM(
                    title=advertisement.title,
                    description=advertisement.description,
                    price=advertisement.price,
                    url=advertisement.url,
                )
                session.add(advertisement_orm)
                session.commit()
            except Exception:
                session.rollback()
                raise

    def get_advertisements(self) -> list[AdvertisementORM]:
        with self.sessionmaker as session:
            return session.execute(select(AdvertisementORM)).scalars_all()

    def update_advertisement(self, advertisement: Advertisement) -> None:
        with self.sessionmaker as session:
            try:
                advertisement_orm = session.execute(
                    select(AdvertisementORM).where(AdvertisementORM.url == advertisement.url),
                )
                if advertisement_orm:
                    advertisement_orm.title = advertisement.title
                    advertisement_orm.description = advertisement.description
                    advertisement_orm.price = advertisement.price
                    session.commit()
                else:
                    raise ValueError(f"Advertisement with url {advertisement.url} not found")
            except Exception:
                session.rollback()
                raise
