from aiogram import types
from aiogram.dispatcher import FSMContext

from bot.handlers.keyboard import get_markup
from bot.handlers.states import ChooseTripState
from bot.handlers.utils import generate_final_route


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
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
    data = await state.get_data()
    route = generate_final_route(data["departure_place"], message.text)

    await message.answer(f"Конечный маршрут: {route}")
    await state.finish()
