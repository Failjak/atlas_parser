from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram_datepicker import Datepicker
from bson import ObjectId

from bot.constants import DEFAULT_INTERVAL, TripConfigureType, ConfigureInterval
from bot.handlers.base.constants import CHANGE_INTERVAL_MESSAGE
from bot.handlers.base.states import ChooseTripState, ChooseTripSearchState, TripConfigureState
from bot.handlers.keyboard import get_markup, generate_trips_inline_markup, \
    generate_trip_settings_inline_markup, configure_button_to_markups
from bot.services.trip_search import stop_all_tips_searching
from bot.settings import _get_datepicker_settings
from services.atlas.atlas_api import AtlasAPI
from services.atlas.dto import LookingTripParams
from services.atlas.exceptions import InvalidCity
from services.mongo.mongo import Mongo
from services.mongo.settings import MongoSettings


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

    mongo = Mongo(settings=MongoSettings())
    mongo.put_param(data=params.dict())
    return await message.answer(f"Параметры поиска сохранены: {params.full_path}")


async def choose_trip_to_start_searching(message: types.Message, **kwargs):
    chat_id = message.chat.id

    mongo = Mongo(settings=MongoSettings())
    params = mongo.get_params(chat_id=chat_id)
    markup = generate_trips_inline_markup(params)
    await message.answer("Доступные маршруты:", reply_markup=markup)
    await ChooseTripSearchState.choose_trip.set()


async def handle_chosen_trip(callback: types.CallbackQuery, **kwargs):
    if not ObjectId.is_valid(callback.data):
        return await callback.answer(callback.data)

    mongo = Mongo(settings=MongoSettings())
    param: LookingTripParams = mongo.retrieve_param(param_id=callback.data)
    if not param or not isinstance(param, LookingTripParams):
        return await callback.answer("Параметры не найдены")

    markup = generate_trip_settings_inline_markup(param)
    await callback.message.edit_text(param.full_path, reply_markup=markup)
    await ChooseTripSearchState.configure_trip.set()


async def handle_configure_for_trip(callback: types.CallbackQuery, **kwargs):
    try:
        data = eval(callback.data)
        if not isinstance(data, dict):
            raise TypeError
    except TypeError:
        return await callback.answer("Ошибка, попробуйте еще раз")

    match data['type']:
        case TripConfigureType.INTERVAL.value:
            markup_generator = configure_button_to_markups.get(TripConfigureType.INTERVAL.value)
            await callback.message.edit_text(
                CHANGE_INTERVAL_MESSAGE.format(data.get('interval', DEFAULT_INTERVAL)),
                reply_markup=markup_generator(**data)
            )
            await TripConfigureState.interval_config_trip.set()

        case TripConfigureType.STATE.value:
            await TripConfigureState.state_config_trip.set()


async def handle_interval_config_for_trip(callback: types.CallbackQuery, **kwargs):
    new_interval = ConfigureInterval.get(callback.data)
    interval = int(new_interval.name.split("_")[1])
    # TODO use api to change request interval


async def handle_state_config_for_trip(callback: types.CallbackQuery, **kwargs):
    try:
        data = eval(callback.data)
        if not isinstance(data, dict):
            raise TypeError
    except TypeError:
        return await callback.answer("Ошибка, попробуйте еще раз")

    # state = data['state']
    #
    # new_state: LookingTripState = change_searching_trip_state(state)
    # if new_state == LookingTripState.ON:
    #     # start_searching_trip(callback.message, param)
    #     await callback.answer("Поиск запущен")
    # elif new_state == LookingTripState.OFF:
    #     # stop_trip_searching(param)
    #     await callback.answer("Поиск остановлен")
    #
    # markup = callback.message.reply_markup
    # change_markup_button_text_by_callback(markup, callback.data, new_state.value)
