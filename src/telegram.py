import asyncio
import logging
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, Filter
from aiogram.filters.command import CommandObject
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import Message
from aiogram.types.bot_command import BotCommand
from aiogram.types.error_event import ErrorEvent
from aiogram.types.input_file import FSInputFile

from client import KufarClient
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID
from dependencies import get_service
from exceptions import KufarScraperError
from exporters import ExcelExporter, GoogleSheetsExporter
from logger import setup_logging
from schemas import AdvertisementDto, AdvertisementHistoryDto


class OwnerFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return (
            message.chat.type == "private"
            and message.from_user is not None
            and message.from_user.id == TELEGRAM_USER_ID
        )


dp = Dispatcher()
dp.message.filter(OwnerFilter())
logger = logging.getLogger(__name__)


def log_message(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            res = await func(*args, **kwargs)
            logger.info("Message successfully sent")
            return res
        except TelegramNetworkError:
            logger.exception("Unable to send message")

    return wrapper


def sync_ads() -> None:
    with get_service() as service, KufarClient() as client:
        service.sync_ads_to_db(client)


@dp.message(Command("sync"))
@log_message
async def sync_handler(message: Message):
    await message.answer("Syncing ads to database...")
    await asyncio.to_thread(sync_ads)
    await message.answer("Ads synced successfully!")


def create_excel_report() -> Path:
    with get_service() as service:
        return service.export_ads(ExcelExporter())


@dp.message(Command("excel"))
@log_message
async def excel_handler(message: Message):
    await message.answer("Exporting ads to Excel...")
    excel_path = await asyncio.to_thread(create_excel_report)
    logger.info("Sending excel through telegram...")
    await message.answer_document(
        document=FSInputFile(excel_path),
        caption="Excel report generated successfully!",
    )
    logger.info("Message sent successfully")


def export_to_google_sheets() -> str:
    with get_service() as service:
        return service.export_ads(GoogleSheetsExporter())


@dp.message(Command("sheets"))
@log_message
async def sheets_handler(message: Message):
    await message.answer("Exporting ads to Google Sheets...")
    sheet_url = await asyncio.to_thread(export_to_google_sheets)
    text = (
        "Ads exported to Google Sheets successfully!\n\n"
        f"<a href='{sheet_url}'>Open Google Sheet</a>"
    )
    await message.answer(
        text,
        disable_web_page_preview=False,
    )


def get_ads() -> list[AdvertisementDto]:
    with get_service() as service:
        return service.get_all_ads_from_db()


@dp.message(Command("ads"))
@log_message
async def ads_handler(message: Message):
    await message.answer("Getting ads...")
    ads = await asyncio.to_thread(get_ads)
    if not ads:
        await message.answer("No ads found in database.")
        return
    for ad in ads:
        await message.answer(str(ad), parse_mode=None)
    await message.answer("Ads sent successfully")


def get_advertisement_history(advertisement_id: int) -> list[AdvertisementHistoryDto]:
    with get_service() as service:
        return service.get_advertisement_history(advertisement_id=advertisement_id)


@dp.message(Command("history"))
@log_message
async def history_handler(message: Message, command: CommandObject):
    if not command.args:
        await message.answer("Please provide an advertisement ID.")
        return

    try:
        advertisement_id = int(command.args)
    except ValueError:
        await message.answer("Advertisement ID must be a number.")
        return

    if advertisement_id <= 0:
        await message.answer("Advertisement ID must be a positive number.")
        return
    await message.answer("Getting advertisement history...")

    ad_history = await asyncio.to_thread(
        get_advertisement_history, advertisement_id=advertisement_id
    )
    if not ad_history:
        await message.answer("No advertisement history found.")
        return
    for snapshot in ad_history:
        await message.answer(str(snapshot), parse_mode=None)

    await message.answer("Advertisement history retrieved successfully!")


@dp.error(ExceptionTypeFilter(TelegramNetworkError))
async def telegram_network_error_handler(event: ErrorEvent):
    if event.update.message is not None:
        logger.exception("Telegram network error occurred")


@dp.error(ExceptionTypeFilter(KufarScraperError))
async def scraper_error_handler(event: ErrorEvent):
    if event.update.message is not None:
        await event.update.message.answer(str(event.exception))


async def create_bot():
    setup_logging("telegram")
    logger.info("Starting Telegram bot...")
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set!")
    if not TELEGRAM_USER_ID:
        raise RuntimeError("TELEGRAM_USER_ID not set!")
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands(
        [
            BotCommand(command="sync", description="Sync ads to database"),
            BotCommand(command="excel", description="Export ads to Excel"),
            BotCommand(command="sheets", description="Export ads to Google Sheets"),
            BotCommand(command="ads", description="Get all ads"),
            BotCommand(command="history", description="Get advertisement history"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(create_bot())
