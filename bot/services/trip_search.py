from aiogram import types
from loguru import logger

from bot.constants import LookingTripState
from bot.decorators import get_api
from services.atlas.atlas_api import AtlasAPI
from services.atlas.dto import LookingTripParams
from services.atlas.scheduler import scheduler


def start_searching_trip(message: types.Message, param: LookingTripParams):
    logger.debug(f"The trip search {param.id} added to pool")

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
        logger.debug(f"The trip search {param.id} has stopped")
        scheduler.remove_job(str(param.id))


def stop_all_tips_searching():
    scheduler.remove_all_jobs()


# def is_job_running(param: LookingTripParams):
#     return LookingTripState.ON if scheduler.get_job(str(param.id)) else LookingTripState.OFF


def change_searching_trip_state(curr_state: LookingTripState) -> LookingTripState:
    return LookingTripState.ON if curr_state == LookingTripState.OFF else LookingTripState.OFF


@get_api
async def trip_searching(message: types.Message, api: AtlasAPI, params: LookingTripParams):
    logger.debug(f"Getting trips to chat_id: {message.chat.id}, by params.id: {params.id}")
    res = await api.get_all_trips(params.departure_city, params.arrival_city, params.date)
    logger.debug(f"Got a response to chat_id: {message.chat.id}, by params.id: {params.id}")
    await message.answer(f"Результат поиска: {res}")
