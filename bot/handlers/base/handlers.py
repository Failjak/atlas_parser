from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram_datepicker import Datepicker
from bson import ObjectId

from bot.constants import DEFAULT_INTERVAL, LookingTripState
from bot.handlers.base.states import ChooseTripState, ChooseTripSearch
from bot.handlers.keyboard import get_markup, generate_trip_params_inline_markup, change_markup_button_text_by_callback
from bot.services.trip_search import start_searching_trip, change_searching_trip_state, stop_trip_searching, \
    stop_all_tips_searching
from bot.settings import _get_datepicker_settings
from services.atlas.atlas_api import AtlasAPI
from services.atlas.dto import LookingTripParams
from services.atlas.exceptions import InvalidCity
from services.mongo.mongo import Mongo
from services.mongo.settings import mongo_settings


async def cmd_start(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    dispatcher = Dispatcher.get_current()

    data = await dispatcher.storage.get_data(chat=chat_id)
    if data.get("interval") is None:
        await state.finish()
        await dispatcher.storage.set_data(chat=chat_id, data={"interval": DEFAULT_INTERVAL})

    markup = get_markup()
    await message.answer("Atlas Schedule Menu:", reply_markup=markup)


async def cmd_stop(message: types.Message, **kwargs):
    stop_all_tips_searching()
    await message.answer("Поиск билетов остановлен")


async def start_trip_adding(message: types.Message):
    await ChooseTripState.place_of_departure.set()
    await message.answer("Место отправления:")


async def set_departure_place(message: types.Message, state: FSMContext, **kwargs):
    await state.update_data(departure_place=message.text)
    await ChooseTripState.place_of_arrival.set()
    await message.answer(f"Место назначения:")


async def set_arrival_place(message: types.Message, state: FSMContext, **kwargs):
    await state.update_data(arrival_place=message.text)
    await ChooseTripState.select_date.set()

    datepicker = Datepicker(_get_datepicker_settings())
    markup = datepicker.start_calendar()
    await message.answer("Выберите дату отправления:", reply_markup=markup)


async def _process_datepicker(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    datepicker = Datepicker(_get_datepicker_settings())

    date = await datepicker.process(callback_query, callback_data)
    if date:
        await state.update_data(date=date)
        await _save_params(callback_query.message)
    else:
        await callback_query.answer()


async def _save_params(message: types.Message):
    chat_id = message.chat.id

    dispatcher = Dispatcher.get_current()
    memory = await dispatcher.storage.get_data(chat=chat_id)

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
    )

    mongo = Mongo(settings=mongo_settings)
    mongo.put_param(data=params.dict())
    return await message.answer(f"Параметры поиска сохранены: {params.full_path}")


async def choose_trip_to_start_searching(message: types.Message, **kwargs):
    chat_id = message.chat.id

    mongo = Mongo(settings=mongo_settings)
    params = mongo.get_params(chat_id=chat_id)
    markup = generate_trip_params_inline_markup(params)
    await message.answer("Доступные маршруты:", reply_markup=markup)
    await ChooseTripSearch.choose_trip.set()


async def handle_chosen_trip(callback: types.CallbackQuery, **kwargs):
    if not ObjectId.is_valid(callback.data):
        return await callback.answer(callback.data)
        # return await callback.answer("Что-то не то. Попробуйте еще раз")

    mongo = Mongo(settings=mongo_settings)
    param: LookingTripParams = mongo.retrieve_param(param_id=callback.data)
    if not param or not isinstance(param, LookingTripParams):
        return await callback.answer("Параметры не найдены")

    new_state: LookingTripState = change_searching_trip_state(param.state)
    if new_state == LookingTripState.ON:
        start_searching_trip(callback.message, param)
        await callback.answer("Поиск запущен")
    elif new_state == LookingTripState.OFF:
        stop_trip_searching(param)
        await callback.answer("Поиск остановлен")

    markup = callback.message.reply_markup
    change_markup_button_text_by_callback(markup, callback.data, new_state.value)
    await callback.message.edit_text(callback.message.text, reply_markup=markup)
