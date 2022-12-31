import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram_datepicker import Datepicker
from loguru import logger

from bot.constants import DEFAULT_INTERVAL
from bot.handlers.base.states import ChooseTripState
from bot.handlers.base.utils import generate_final_route
from bot.handlers.keyboard import get_markup
from bot.settings import _get_datepicker_settings
from services.atlas.atlas_api import AtlasAPI
from services.atlas.dto import DateTrips
from services.atlas.exceptions import InvalidCity, TooFrequentRequests
from services.atlas.types import CityType
from services.parser.dto import ParserDto


async def cmd_start(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    dispatcher = Dispatcher.get_current()

    data = await dispatcher.storage.get_data(chat=chat_id)
    if data.get("interval") is None:
        await state.finish()
        await dispatcher.storage.set_data(chat=chat_id, data={"interval": DEFAULT_INTERVAL})

    markup = get_markup()
    await message.answer("Atlas Schedule Menu:", reply_markup=markup)


async def cmd_stop(message: types.Message, state: FSMContext):
    await state.update_data(is_run=False)
    await message.answer("Поиск билетов остановлен")


async def start_trip_choosing(message: types.Message):
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
        await info_presentation(message=callback_query.message, state=state)
    else:
        await callback_query.answer()


async def info_presentation(message: types.Message, state: FSMContext, **kwargs):
    chat_id = message.chat.id
    dispatcher = Dispatcher.get_current()
    memory = await dispatcher.storage.get_data(chat=chat_id)

    parser_dto = ParserDto(
        send_only_if_exist=True,
        departure_place=memory.get("departure_place"),
        arrival_place=memory.get("arrival_place"),
        date=memory.get("date"),
        interval=memory.get("interval", DEFAULT_INTERVAL)
    )

    route = generate_final_route(parser_dto)
    await message.answer(f"Конечный маршрут: {route}")

    await state.update_data(is_run=True)
    logger.log("BOT", f"Start parsing for chat_id: `{chat_id}`")

    api = AtlasAPI()
    try:
        dep_city = await api.get_city_by_name(city_name=parser_dto.departure_place, city_type=CityType.DEPARTURE)
        arrival_city = await api.get_city_by_name(from_id=dep_city.id, city_name=parser_dto.arrival_place, city_type=CityType.ARRIVAL)

        while (await dispatcher.storage.get_data(chat=chat_id)).get("is_run"):
            trips = await api.get_all_trips(dep_city, arrival_city, parser_dto.date)
            logger.log("BOT", f"(chat_id: `{chat_id}`) Received a response from the API: {trips}")

            await asyncio.sleep(parser_dto.interval * 60)

            if parser_dto.send_only_if_exist:
                if type(trips) == DateTrips:
                    await message.answer(trips)
            else:
                await message.answer(trips)

    except (InvalidCity, TooFrequentRequests) as e:
        await message.answer(e.msg)
    finally:
        await state.update_data(is_run=False)

    logger.log("BOT", f"Parsing for chat_id: `{chat_id}` has been stopped")
    await state.finish()
