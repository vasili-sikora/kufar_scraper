from dataclasses import dataclass


@dataclass
class Advertisement:
    title: str
    description: str
    price: str
    url: str

    def __repr__(self) -> str:
        return f"<Advertisement title={self.title} price={self.price}>"

    def __str__(self) -> str:
        return f"{self.title} - {self.price}"
