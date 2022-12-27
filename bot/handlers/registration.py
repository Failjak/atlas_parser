from aiogram import Dispatcher

from bot.handlers.handlers import cmd_start, start_trip_choosing, set_arrival_place, set_departure_place
from bot.handlers.keyboard import BaseCommands
from bot.handlers.states import ChooseTripState


def registration_handlers(dp: Dispatcher):
    dp.register_message_handler(
        callback=cmd_start, commands=['start'], state='*'
    )

    dp.register_message_handler(
        start_trip_choosing, lambda m: m.text == BaseCommands.CHOOSE_TRIP.value, state='*'
    )
    # lambda c: c.data == "Добавление маршрута",
    dp.register_message_handler(
        set_departure_place, state=ChooseTripState.place_of_departure
    )
    dp.register_message_handler(
        callback=set_arrival_place, state=ChooseTripState.place_of_arrival,
    )
