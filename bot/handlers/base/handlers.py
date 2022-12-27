import asyncio

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram_datepicker import Datepicker

from bot.constants import DEFAULT_INTERVAL
from bot.handlers.keyboard import get_markup
from bot.handlers.base.states import ChooseTripState
from bot.handlers.base.utils import generate_final_route
from bot.settings import _get_datepicker_settings
from parser.dto import ParserDto
from parser.parser import run_parser
from parser.settings import parser_settings


async def cmd_start(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    dispatcher = Dispatcher.get_current()

    data = await dispatcher.storage.get_data(chat=chat_id)
    if data.get("interval") is None:
        await state.finish()
        await dispatcher.storage.set_data(chat=chat_id, data={"interval": DEFAULT_INTERVAL})

    markup = get_markup()
    await message.answer("Atlas Schedule Menu:", reply_markup=markup)


async def cmd_stop(message: types.Message):
    chat_id = message.chat.id
    dispatcher = Dispatcher.get_current()
    await dispatcher.storage.set_data(chat=chat_id, data={"run": False})


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
        date = date.strftime('%Y-%m-%d')
        await callback_query.message.answer(date)
        await state.update_data(date=date)
        await info_presentation(message=callback_query.message, state=state)
    else:
        await callback_query.answer()


async def info_presentation(message: types.Message, state: FSMContext, **kwargs):
    chat_id = message.chat.id
    dispatcher = Dispatcher.get_current()
    memory = await dispatcher.storage.get_data(chat=chat_id)

    parser_dto = ParserDto(
        departure_place=memory.get("departure_place"),
        arrival_place=memory.get("arrival_place"),
        date=memory.get("date"),
        interval=memory.get("interval", DEFAULT_INTERVAL)
    )

    route = generate_final_route(parser_dto)
    await message.answer(f"Конечный маршрут: {route}")

    while memory.get("run", True):
        await run_parser(parser_settings, parser_dto)
        await asyncio.sleep(parser_dto.interval * 60)
        memory = await dispatcher.storage.get_data(chat=chat_id)

    await state.finish()
