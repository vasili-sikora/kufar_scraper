import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    DATABASE_URL: str
    USER_URL: str
    BEARER_TOKEN: str


def load_config() -> Config:
    database_url = os.getenv("DATABASE_URL")
    user_url = os.getenv("USER_URL")
    bearer_token = os.getenv("BEARER_TOKEN")

    if not database_url:
        raise ValueError("DATABASE_URL is not set in .env")
    if not user_url:
        raise ValueError("USER_URL is not set in .env")
    if not bearer_token:
        raise ValueError("BEARER_TOKEN is not set in .env")

    return Config(
        DATABASE_URL=database_url,
        USER_URL=user_url,
        BEARER_TOKEN=bearer_token,
    )
