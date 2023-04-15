from aiogram import Dispatcher
from aiogram_datepicker import Datepicker

from bot.handlers.base import handlers as base_handlers
from bot.handlers.base.states import CreateTripState, ChooseTripSearchState, TripConfigureState
from bot.handlers.keyboard import BaseCommands
from bot.handlers.trip import handlers as trip_handlers


def registration_handlers(dp: Dispatcher):
    dp.register_message_handler(
        callback=base_handlers.cmd_start, commands=['start'], state='*'
    )
    # dp.register_message_handler(  # TODO dont work, why ?
    #     cmd_stop, lambda m: m.text == BaseCommands.STOP_LOOKING, state='*'
    # )

    dp.register_message_handler(
        base_handlers.start_trip_adding, lambda m: m.text == BaseCommands.ADD_TRIP.value, state='*'
    )
    dp.register_message_handler(
        base_handlers.set_departure_place, state=CreateTripState.place_of_departure
    )
    dp.register_message_handler(
        callback=base_handlers.set_arrival_place, state=CreateTripState.place_of_arrival,
    )

    dp.register_callback_query_handler(
        base_handlers._process_datepicker, Datepicker.datepicker_callback.filter(), state=CreateTripState.select_date,
    )

    dp.register_message_handler(
        trip_handlers.choose_trip_to_start_searching, lambda m: m.text == BaseCommands.CHOOSE_TRIP.value, state='*'
    )
    dp.register_callback_query_handler(
        trip_handlers.handle_chosen_trip, lambda c: c.data, state=ChooseTripSearchState.choose_trip
    )
    dp.register_callback_query_handler(
        trip_handlers.handle_configure_for_trip, lambda c: c.data, state=ChooseTripSearchState.configure_trip
    )

    dp.register_callback_query_handler(
        trip_handlers.handle_interval_config_for_trip, state=TripConfigureState.interval_config_trip,
    )


def register_back_button_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        trip_handlers.handle_configure_trip_back_button,
        lambda c: c.data == 'configure_trip_back',
        state=ChooseTripSearchState.configure_trip
    )
    dp.register_callback_query_handler(
        trip_handlers.handle_trip_interval_config_back_button,
        lambda c: c.data == 'trip_interval_config',
        state=TripConfigureState.interval_config_trip
    )
