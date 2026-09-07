import asyncio

from kufar_scraper.cli import choose_option


async def main():
    await choose_option()


if __name__ == "__main__":
    asyncio.run(main())
