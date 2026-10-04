from dataclasses import dataclass
from datetime import datetime

from models import AdvertisementOrm


@dataclass(slots=True)
class AdvertisementItem:
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
    def from_orm(cls, ad: AdvertisementOrm) -> AdvertisementItem:
        return cls(
            ad.kufar_id,
            ad.title,
            ad.price,
            ad.status,
            ad.link,
            ad.published_at,
            ad.description,
        )
