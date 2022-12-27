from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData
from aiogram_datepicker import Datepicker

from bot.handlers.keyboard import get_markup
from bot.handlers.base.states import ChooseTripState
from bot.handlers.base.utils import generate_final_route
from bot.settings import _get_datepicker_settings
from parser.dto import ParserDto
from parser.parser import run_parser
from parser.settings import parser_settings


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()

    user_id = message.from_user.id
    dispatcher = Dispatcher.get_current()
    await dispatcher.storage.set_data(user=user_id, data={"interval": 120})

    markup = get_markup()
    await message.answer("Atlas Schedule Menu:", reply_markup=markup)


async def start_trip_choosing(message: types.Message, state: FSMContext):
    user_id = message.from_id
    await state.update_data(user_id=user_id)
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

    await callback_query.answer()


async def info_presentation(message: types.Message, state: FSMContext, **kwargs):
    data = await state.get_data()

    user_id = message.from_user.id
    dispatcher = Dispatcher.get_current()
    memory = await dispatcher.storage.get_data(user=user_id)

    parser_dto = ParserDto(departure_place=data.get("departure_place"), arrival_place=data.get("arrival_place"),
                           date=data.get("date"), interval=memory.get("interval", 300))

    route = generate_final_route(parser_dto)
    await message.answer(f"Конечный маршрут: {route}")

    async for info in run_parser(settings=parser_settings, params=parser_dto):
        if info: await message.answer(info)

    await state.finish()
