from aiogram import Dispatcher
from aiogram_datepicker import Datepicker

from bot.handlers.base.handlers import cmd_start, start_trip_adding, set_arrival_place, set_departure_place, \
    _process_datepicker, cmd_stop, choose_trip_to_start_searching, handle_chosen_trip
from bot.handlers.base.states import ChooseTripState, ChooseTripSearch
from bot.handlers.configure.handlers import configurations, _process_configurations
from bot.handlers.configure.states import ConfigureState
from bot.handlers.keyboard import BaseCommands


def registration_handlers(dp: Dispatcher):
    dp.register_message_handler(
        callback=cmd_start, commands=['start'], state='*'
    )
    dp.register_message_handler(
        cmd_stop, lambda m: m.text == BaseCommands.STOP_LOOKING, commands=['stop'], state='*'
    )

    dp.register_message_handler(
        start_trip_adding, lambda m: m.text == BaseCommands.ADD_TRIP.value, state='*'
    )
    dp.register_message_handler(
        set_departure_place, state=ChooseTripState.place_of_departure
    )
    dp.register_message_handler(
        callback=set_arrival_place, state=ChooseTripState.place_of_arrival,
    )

    dp.register_callback_query_handler(
        _process_datepicker, Datepicker.datepicker_callback.filter(), state=ChooseTripState.select_date,
    )

    dp.register_message_handler(
        choose_trip_to_start_searching, lambda m: m.text == BaseCommands.CHOOSE_TRIP.value, state='*'
    )
    dp.register_callback_query_handler(
        handle_chosen_trip, lambda c: c.data, state=ChooseTripSearch.choose_trip
    )


def register_callback_configure_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        _process_configurations, state=ConfigureState.choose_configure,
    )


def register_configure_handlers(dp: Dispatcher):
    dp.register_message_handler(
        configurations, lambda m: m.text == BaseCommands.CONFIGURATION.value, state="*"
    )
    register_callback_configure_handlers(dp)
