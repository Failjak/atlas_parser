from typing import List

from aiogram import types

from bot.constants import LookingTripState
from bot.handlers.keyboard import generate_trips_inline_markup, generate_trip_settings_inline_markup, add_button
from services.atlas.dto import LookingTripParams
from services.mongo.mongo import Mongo
from services.mongo.settings import MongoSettings


def generate_choose_trip_info(chat_id: str):
    mongo = Mongo(settings=MongoSettings())
    params: List[LookingTripParams] = mongo.retrieve_trips_params(chat_id=chat_id)

    text = "Доступные маршруты:"
    markup = generate_trips_inline_markup(params)

    if not markup.inline_keyboard:
        add_button(markup, 'Нет доступных маршрутов', 'Добавьте маршруты')

    return text, markup


def generate_trip_info(trip_id: str):
    mongo = Mongo(settings=MongoSettings())
    param: LookingTripParams = mongo.retrieve_trip_params(trip_id=trip_id)
    if not param or not isinstance(param, LookingTripParams):
        return 'Параметры не найдены', None

    return param.title, generate_trip_settings_inline_markup(param)


async def process_state_config_for_trip(message: types.Message, trip_id: str):
    from bot.services import trip_search

    mongo = Mongo(settings=MongoSettings())
    trip_params: LookingTripParams = mongo.update_trip_state(trip_id)

    if trip_params.state == LookingTripState.ON:
        trip_search.start_searching_trip(message, trip_params)
    elif trip_params.state == LookingTripState.OFF:
        trip_search.stop_trip_searching(trip_params)

    return trip_params.title, generate_trip_settings_inline_markup(trip_params)
