from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...


class AdvertisementOrm(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(primary_key=True)
    kufar_id: Mapped[int] = mapped_column(unique=True, index=True)
    title: Mapped[str]
    description: Mapped[str | None]
    price: Mapped[float]
    status: Mapped[str]
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    link: Mapped[str]
