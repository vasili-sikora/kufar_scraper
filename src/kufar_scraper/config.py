import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass
class Config:
    DATABASE_URL: str
    USER_URL: str


def load_config() -> Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    USER_URL = os.getenv("USER_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env")
    if not USER_URL:
        raise ValueError("USER_URL is not set in .env")

    return Config(
        DATABASE_URL=DATABASE_URL,
        USER_URL=USER_URL,
    )
