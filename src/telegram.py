import asyncio
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, Filter
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.types import Message
from aiogram.types.bot_command import BotCommand
from aiogram.types.error_event import ErrorEvent
from aiogram.types.input_file import FSInputFile

from client import KufarClient
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_USER_ID
from dependencies import get_service
from exceptions import KufarScraperError
from schemas import AdvertisementHistoryDto


class OwnerFilter(Filter):
    async def __call__(self, message: Message) -> bool:
        return (
            message.chat.type == "private"
            and message.from_user is not None
            and message.from_user.id == TELEGRAM_USER_ID
        )


dp = Dispatcher()
dp.message.filter(OwnerFilter())


def sync_ads() -> None:
    with get_service() as service, KufarClient() as client:
        service.sync_ads_to_db(client)


@dp.message(Command("sync"))
async def sync_handler(message: Message):
    await message.answer("Syncing ads to database...")
    await asyncio.to_thread(sync_ads)
    await message.answer("Ads synced successfully!")


def create_excel_report() -> Path:
    with get_service() as service:
        return service.save_to_excel()


@dp.message(Command("excel"))
async def excel_handler(message: Message):
    await message.answer("Exporting ads to Excel...")
    excel_path = await asyncio.to_thread(create_excel_report)
    await message.answer_document(
        document=FSInputFile(excel_path),
        caption="Excel report generated successfully!",
    )


def get_advertisement_history() -> list[AdvertisementHistoryDto]:
    with get_service() as service:
        return service.get_advertisement_history(advertisement_id=1079214458)


@dp.message(Command("history"))
async def history_handler(message: Message):
    await message.answer("Getting advertisement history...")

    ad_history = await asyncio.to_thread(get_advertisement_history)
    if not ad_history:
        await message.answer("No advertisement history found.")
        return
    for snapshot in ad_history:
        await message.answer(str(snapshot), parse_mode=None)

    await message.answer("Advertisement history retrieved successfully!")


@dp.error(ExceptionTypeFilter(TelegramNetworkError))
async def telegram_network_error_handler(event: ErrorEvent):
    if event.update.message is not None:
        await event.update.message.answer(
            "Telegram network error occurred. Please try again later."
        )


@dp.error(ExceptionTypeFilter(KufarScraperError))
async def scraper_error_handler(event: ErrorEvent):
    if event.update.message is not None:
        await event.update.message.answer(str(event.exception))


async def create_bot():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN not set!")
    if not TELEGRAM_USER_ID:
        raise RuntimeError("TELEGRAM_USER_ID not set!")
    bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await bot.set_my_commands(
        [
            BotCommand(command="sync", description="Sync ads to database"),
            BotCommand(command="excel", description="Export ads to Excel"),
            BotCommand(command="history", description="Get advertisement history"),
        ]
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(create_bot())
