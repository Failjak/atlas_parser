from aiogram.dispatcher.filters.state import State, StatesGroup


class ChooseTripState(StatesGroup):
    place_of_departure = State()
    place_of_arrival = State()
    select_date = State()
    send_info = State()


class ChooseTripSearchState(StatesGroup):
    choose_trip = State()
    configure_trip = State()


class TripConfigureState(StatesGroup):
    interval_config_trip = State()
    state_config_trip = State()
