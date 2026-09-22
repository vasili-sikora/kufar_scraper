from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class AdvertisementItem:
    kufar_id: int
    title: str
    price: float
    status: str
    link: str
    published_at: datetime
    description: str | None = None
