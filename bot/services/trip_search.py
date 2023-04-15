from aiogram import types
from loguru import logger

from bot import emojies
from bot.constants import LookingTripState
from bot.decorators import get_api
from services.atlas.atlas_api import AtlasAPI
from services.atlas.dto import LookingTripParams
from services.atlas.scheduler import scheduler


def start_searching_trip(message: types.Message, param: LookingTripParams):
    logger.log("BOT", f"The trip search {param.id} added to pool")

    scheduler.add_job(
        trip_searching,
        id=str(param.id),
        kwargs={"message": message, "params": param},
        trigger="interval",
        seconds=param.interval * 60,
        coalesce=True,
    )

    if not scheduler.state:
        scheduler.start()


def stop_trip_searching(param: LookingTripParams):
    if scheduler.get_job(str(param.id)):
        logger.log("BOT", f"The trip search {param.id} has stopped")
        scheduler.remove_job(str(param.id))


async def notify_job_users(jobs, msg: str):
    users = set()
    for job in jobs:
        message = job.kwargs.get('message')
        if not message or message and message.from_id in users:
            continue
        users.add(message.from_id)
        await message.answer(msg)


async def stop_all_tips_searching():
    await notify_job_users(
        scheduler.get_jobs(),
        f"{emojies.EXCLAMATION_MARK} Технические неполадки, все задачи были остановлены {emojies.EXCLAMATION_MARK}"
    )
    scheduler.remove_all_jobs()


# def is_job_running(param: LookingTripParams):
#     return LookingTripState.ON if scheduler.get_job(str(param.id)) else LookingTripState.OFF


def change_searching_trip_state(curr_state: LookingTripState) -> LookingTripState:
    return LookingTripState.ON if curr_state == LookingTripState.OFF else LookingTripState.OFF


@get_api
async def trip_searching(message: types.Message, api: AtlasAPI, params: LookingTripParams):
    logger.log("BOT", f"Getting trips to chat_id: {message.chat.id}, by params.id: {params.id}")
    res = await api.get_all_trips(params.departure_city, params.arrival_city, params.date)
    logger.info("BOT", f"Got a response to chat_id: {message.chat.id}, by params.id: {params.id}")
    await message.answer(f"Результат поиска: {res}")
