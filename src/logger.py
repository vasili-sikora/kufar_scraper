import datetime
from collections.abc import Callable
from functools import wraps
from typing import Any

from config import LOGS_FILEPATH


def log(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with open(file=LOGS_FILEPATH, mode="a", encoding="utf-8") as file:
            try:
                file.write(f"[INFO] [{datetime.datetime.now(tz=datetime.UTC)}]: {func.__name__}\n")
                res = func(*args, **kwargs)
                file.write(f"{func.__name__} успешно завершилась\n")
                return res
            except Exception as e:
                file.write(f"[ERROR]: {func.__name__}: {e!s}\n")
                raise

    return wrapper
