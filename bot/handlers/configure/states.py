from aiogram.dispatcher.filters.state import State, StatesGroup


class ConfigureState(StatesGroup):
    choose_configure = State()
    interval = State()
