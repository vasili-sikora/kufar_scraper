from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase): ...

class AdvertisementORM(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    kufar_id: Mapped[int]
    title: Mapped[str]
    description: Mapped[str]
    price: Mapped[str]
    url: Mapped[str]
