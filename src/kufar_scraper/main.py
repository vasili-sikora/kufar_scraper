import asyncio

from kufar_scraper.cli import print_advertisements, update_advertisements_in_db


async def main():
    await update_advertisements_in_db()
    print_advertisements()


if __name__ == "__main__":
    asyncio.run(main())
