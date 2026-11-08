import asyncio
import logging
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

import httpx
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
from config import CRON_INTERVAL_HOURS, TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID
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
        message = next((arg for arg in args if isinstance(arg, Message)), None)
        user_info = (
            f"user_id={message.from_user.id}" if message and message.from_user else "unknown_user"
        )
        try:
            res = await func(*args, **kwargs)
            logger.info("Command /%s executed successfully for %s", func.__name__, user_info)
            return res
        except TelegramNetworkError:
            logger.exception("Telegram network error during /%s for %s", func.__name__, user_info)
            raise

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


def export_to_google_sheets() -> str:
    with get_service() as service, KufarClient() as client:
        service.sync_ads_to_db(client)
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


@dp.error()
async def global_error_handler(event: ErrorEvent):
    logger.exception("Unhandled error in bot: %s", event.exception)
    if event.update and event.update.message:
        await event.update.message.answer(
            "An unexpected error occurred while processing your request. Please try again later."
        )


async def scheduled_sync_loop() -> None:
    """Periodic background sync of advertisements and Google Sheets update."""
    if CRON_INTERVAL_HOURS <= 0:
        logger.info("Scheduled sync is disabled (CRON_INTERVAL_HOURS <= 0).")
        return

    interval_seconds = CRON_INTERVAL_HOURS * 3600
    logger.info("Scheduled sync loop active (interval: %d hours).", CRON_INTERVAL_HOURS)

    while True:
        await asyncio.sleep(interval_seconds)
        try:
            logger.info("Starting scheduled sync job in bot...")
            sheet_url = await asyncio.to_thread(export_to_google_sheets)
            logger.info("Scheduled sync job completed successfully.")
            send_telegram_notification(
                f"<b>Cron: Kufar sync completed</b>\n<a href='{sheet_url}'>Open Google Sheet</a>"
            )
        except Exception as e:
            logger.exception("Scheduled sync job failed")
            send_telegram_notification(f"<b>Cron: Kufar sync error</b>\n<code>{e}</code>")


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
    _ = asyncio.create_task(scheduled_sync_loop())
    await dp.start_polling(bot)


def send_telegram_notification(text: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_USER_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_USER_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as e:
        logger.warning("Failed to send telegram notification: %s", e)


if __name__ == "__main__":
    asyncio.run(create_bot())
