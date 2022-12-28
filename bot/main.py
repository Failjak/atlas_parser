from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from loguru import logger

from bot.handlers.registration import registration_handlers, register_configure_handlers
from bot.settings import bot_settings


def main(dispatcher: Dispatcher):
    registration_handlers(dispatcher)
    register_configure_handlers(dispatcher)


def run_bot():
    bot = Bot(token=bot_settings.bot_token)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    main(
        dispatcher=dp,
    )

    logger.info('Start polling')
    executor.start_polling(dp, skip_updates=True)
    logger.info('Finish')
