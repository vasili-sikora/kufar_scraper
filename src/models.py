from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): ...


class AdvertisementOrm(Base):
    __tablename__: str = "advertisements"

    kufar_id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column()
    description: Mapped[str | None] = mapped_column()
    price: Mapped[float] = mapped_column()
    status: Mapped[str] = mapped_column()
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    link: Mapped[str] = mapped_column()

    history: Mapped[list[AdvertisementHistoryOrm]] = relationship(
        back_populates="advertisement",
        cascade="all, delete-orphan",
        order_by="AdvertisementHistoryOrm.changed_at.desc()",
    )


class AdvertisementHistoryOrm(Base):
    __tablename__ = "advertisement_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    kufar_id: Mapped[int] = mapped_column(ForeignKey("advertisements.kufar_id", ondelete="CASCADE"))

    field_name: Mapped[str]
    old_value: Mapped[str | None]
    new_value: Mapped[str]
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(tz=UTC)
    )

    advertisement: Mapped[AdvertisementOrm] = relationship(back_populates="history")
