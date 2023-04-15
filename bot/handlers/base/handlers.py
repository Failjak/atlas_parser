from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram_datepicker import Datepicker

from bot.constants import DEFAULT_INTERVAL, LookingTripState
from bot.handlers.base.states import CreateTripState
from bot.handlers.keyboard import get_markup
from bot.settings import _get_datepicker_settings
from services.atlas.atlas_api import AtlasAPI
from services.atlas.dto import LookingTripParams
from services.atlas.exceptions import InvalidCity
from services.mongo.mongo import Mongo
from services.mongo.settings import MongoSettings


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await state.set_data({"interval": DEFAULT_INTERVAL})

    markup = get_markup()
    await message.answer("Atlas Schedule Menu:", reply_markup=markup)


# async def cmd_stop(message: types.Message, **kwargs):
#     await stop_all_tips_searching()
#     await message.answer("Поиск билетов остановлен")


async def start_trip_adding(message: types.Message):
    await CreateTripState.place_of_departure.set()
    await message.answer("Место отправления:")


async def set_departure_place(message: types.Message, state: FSMContext, **kwargs):
    await state.update_data(departure_place=message.text)
    await CreateTripState.place_of_arrival.set()
    await message.answer(f"Место назначения:")


async def set_arrival_place(message: types.Message, state: FSMContext, **kwargs):
    await state.update_data(arrival_place=message.text)
    await CreateTripState.select_date.set()

    datepicker = Datepicker(_get_datepicker_settings())
    markup = datepicker.start_calendar()
    await message.answer("Выберите дату отправления:", reply_markup=markup)


async def _process_datepicker(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        await state.update_data(date=date)
        await _save_params(callback_query.message, state)
    else:
        await callback_query.answer()


async def _save_params(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    memory = await state.get_data()

    api = AtlasAPI()
    try:
        dep_city = await api.get_departure_city_by_name(city_name=memory.get("departure_place"))
        arrival_city = await api.get_arrival_city_by_name(from_id=dep_city.id, city_name=memory.get("arrival_place"))
    except InvalidCity as e:
        return await message.answer(e.msg)

    params = LookingTripParams(
        departure_city=dep_city,
        arrival_city=arrival_city,
        date=memory.get("date"),
        interval=memory.get("interval", DEFAULT_INTERVAL),
        chat_id=chat_id,
        state=LookingTripState.OFF,
    )

    mongo = Mongo(settings=MongoSettings())
    mongo.put_trip(data=params.dict())
    return await message.answer(f"Параметры поиска сохранены: {params.title}")
