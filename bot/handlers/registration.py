from aiogram import Dispatcher
from aiogram_datepicker import Datepicker

from bot.handlers.base.handlers import cmd_start, start_trip_adding, set_arrival_place, set_departure_place, \
    _process_datepicker
from bot.handlers.base.states import ChooseTripState, ChooseTripSearchState, TripConfigureState
from bot.handlers.configure.handlers import configurations
from bot.handlers.keyboard import BaseCommands
from bot.handlers.trip.handlers import choose_trip_to_start_searching, handle_chosen_trip, handle_configure_for_trip, \
    handle_interval_config_for_trip


def registration_handlers(dp: Dispatcher):
    dp.register_message_handler(
        callback=cmd_start, commands=['start'], state='*'
    )
    # dp.register_message_handler(  # TODO dont work, why ?
    #     cmd_stop, lambda m: m.text == BaseCommands.STOP_LOOKING, state='*'
    # )

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
        handle_chosen_trip, lambda c: c.data, state=ChooseTripSearchState.choose_trip
    )
    dp.register_callback_query_handler(
        handle_configure_for_trip, lambda c: c.data, state=ChooseTripSearchState.configure_trip
    )


def register_callback_configure_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        handle_interval_config_for_trip, state=TripConfigureState.interval_config_trip,
    )


#     dp.register_callback_query_handler(
#         handle_state_config_for_trip, state=TripConfigureState.state_config_trip,
#     )


def register_configure_handlers(dp: Dispatcher):
    dp.register_message_handler(
        configurations, lambda m: m.text == BaseCommands.CONFIGURATION.value, state="*"
    )
    register_callback_configure_handlers(dp)
