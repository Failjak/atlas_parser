import asyncio

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from loguru import logger

from bot.handlers.registration import registration_handlers, register_configure_handlers
from bot.services.trip_search import stop_all_tips_searching
from bot.settings import bot_settings
from services.mongo.mongo import Mongo
from services.mongo.settings import MongoSettings


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

    logger.info('START: Stop and notify all users')
    loop = asyncio.get_event_loop()
    coroutine = stop_all_tips_searching()
    loop.run_until_complete(coroutine)
    logger.info('FINISHED: Stop and notify all users')

    logger.info('START: Updating all trips to the OFF state')
    mongo = Mongo(settings=MongoSettings())
    mongo.update_all_trip_state_to_off()
    logger.info('FINISHED: Updating all trips to the OFF state')

    logger.info('Finish')
