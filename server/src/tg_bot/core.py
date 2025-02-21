from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from project.env import bot_settings

dp = Dispatcher()


async def start_polling() -> None:
    from . import callbacks, commands

    # Initialize Bot instance with default bot properties which will be passed to all API calls

    # And the run events dispatching
    bot = Bot(token=bot_settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


async def start_bot():
    await start_polling()


def run_bot():
    import asyncio
    import logging
    import sys

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(start_bot())
