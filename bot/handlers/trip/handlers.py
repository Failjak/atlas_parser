from typing import List

from aiogram import types
from bson import ObjectId

from bot.constants import TripConfigureType, ConfigureInterval
from bot.handlers.base.constants import CHANGE_INTERVAL_MESSAGE
from bot.handlers.base.states import ChooseTripSearchState, TripConfigureState
from bot.handlers.keyboard import generate_trips_inline_markup, \
    generate_trip_settings_inline_markup, configure_button_to_markups
from services.atlas.dto import LookingTripParams
from services.mongo.mongo import Mongo
from services.mongo.settings import MongoSettings


async def choose_trip_to_start_searching(message: types.Message, **kwargs):
    chat_id = message.chat.id

    mongo = Mongo(settings=MongoSettings())
    params: List[LookingTripParams] = mongo.retrieve_trips_params(chat_id=chat_id)

    markup = generate_trips_inline_markup(params)
    await message.answer("Доступные маршруты:", reply_markup=markup)  # TODO нет доступных маршрутов
    await ChooseTripSearchState.choose_trip.set()


async def handle_chosen_trip(callback: types.CallbackQuery, **kwargs):
    if not ObjectId.is_valid(callback.data):
        return await callback.answer(callback.data)

    mongo = Mongo(settings=MongoSettings())
    param: LookingTripParams = mongo.retrieve_trip_params(trip_id=callback.data)
    if not param or not isinstance(param, LookingTripParams):
        return await callback.answer("Параметры не найдены")

    markup = generate_trip_settings_inline_markup(param)
    await callback.message.edit_text(param.title, reply_markup=markup)
    await ChooseTripSearchState.configure_trip.set()


async def handle_configure_for_trip(callback: types.CallbackQuery, **kwargs):
    try:
        data = eval(callback.data)
        if not isinstance(data, dict):
            raise TypeError
    except TypeError:
        return await callback.answer("Ошибка, попробуйте еще раз")

    match data.pop('type'):
        case TripConfigureType.INTERVAL.value:
            markup_generator = configure_button_to_markups.get(TripConfigureType.INTERVAL.value)
            await callback.message.edit_text(
                CHANGE_INTERVAL_MESSAGE,
                reply_markup=markup_generator(**data)
            )
            await TripConfigureState.interval_config_trip.set()

        case TripConfigureType.STATE.value:
            title, markup = await handle_state_config_for_trip(data)
            await callback.message.edit_text(title, reply_markup=markup)


async def handle_interval_config_for_trip(callback: types.CallbackQuery):
    try:
        data = eval(callback.data)
        if not isinstance(data, dict):
            raise TypeError
    except TypeError:
        return await callback.answer("Ошибка, попробуйте еще раз")

    trip_id = eval(callback.data)['trip_id']
    new_interval = ConfigureInterval.get(data.get('key'))
    interval = int(new_interval.name.split("_")[1])

    mongo = Mongo(settings=MongoSettings())
    mongo.update_trip(trip_id, data={'interval': interval})
    trip_params: LookingTripParams = mongo.retrieve_trip_params(trip_id)

    return trip_params.title, generate_trip_settings_inline_markup(trip_params)


async def handle_state_config_for_trip(data: dict):
    trip_id = data['trip_id']
    mongo = Mongo(settings=MongoSettings())
    trip_params: LookingTripParams = mongo.update_trip_state(trip_id)
    return trip_params.title, generate_trip_settings_inline_markup(trip_params)
