import asyncio
import os
import sys

from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import get_connection_string_bot, get_environ
from db.requests import test_connection
from handlers import get_routers
from middlewares import DbSessionMiddleware




async def main():
    connection_string = get_connection_string_bot()
    engine = create_async_engine(url=connection_string, echo=True)

    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    async with sessionmaker() as session:
        await test_connection(session)

    dp = Dispatcher()

    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))

    dp.include_routers(*get_routers())

    telegram_bot_api_token = get_environ("TELEGRAM_BOT_API_TOKEN")

    bot = Bot(token=telegram_bot_api_token)

    await dp.start_polling(bot)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
