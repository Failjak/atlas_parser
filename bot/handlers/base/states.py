from aiogram.dispatcher.filters.state import State, StatesGroup


class ChooseTripState(StatesGroup):
    place_of_departure = State()
    place_of_arrival = State()
    select_date = State()
    send_info = State()
