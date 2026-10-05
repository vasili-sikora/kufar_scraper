from dataclasses import dataclass
from datetime import datetime

from models import AdvertisementHistoryOrm, AdvertisementOrm


@dataclass(slots=True)
class AdvertisementDto:
    kufar_id: int
    title: str
    price: float
    status: str
    link: str
    published_at: datetime
    description: str | None = None

    def __str__(self) -> str:
        desc_preview = (self.description[:60] + "...") if self.description else "нет описания"
        return (
            f"[{self.status.upper()}] {self.title} — {self.price} BYN\n"
            f"  Спеки/описание: {desc_preview}\n"
            f"  Ссылка: {self.link}"
        )

    @classmethod
    def from_orm(cls, ad: AdvertisementOrm) -> AdvertisementDto:
        return cls(
            ad.kufar_id,
            ad.title,
            ad.price,
            ad.status,
            ad.link,
            ad.published_at,
            ad.description,
        )


@dataclass(slots=True, frozen=True)
class AdvertisementHistoryDto:
    id: int
    kufar_id: int
    field_name: str
    old_value: str | None
    new_value: str
    changed_at: datetime

    def __str__(self) -> str:
        date_str = self.changed_at.strftime("%Y-%m-%d %H:%M")
        return f"[{date_str}] {self.field_name}: '{self.old_value}' -> '{self.new_value}'"

    @classmethod
    def from_orm(cls, ad_history_orm: AdvertisementHistoryOrm) -> AdvertisementHistoryDto:
        return cls(
            id=ad_history_orm.id,
            kufar_id=ad_history_orm.kufar_id,
            field_name=ad_history_orm.field_name,
            old_value=ad_history_orm.old_value,
            new_value=ad_history_orm.new_value,
            changed_at=ad_history_orm.changed_at,
        )
