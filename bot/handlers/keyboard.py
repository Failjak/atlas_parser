from enum import Enum
from typing import List, Generator

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot.constants import ConfigureButtons, ConfigureInterval, TripConfigureType
from services.atlas.dto import LookingTripParams


class BaseCommands(Enum):
    CHOOSE_TRIP = "Выбрать маршрут"
    ADD_TRIP = "Добавить маршрут"
    # STOP_LOOKING = "Остановить поиск всех маршрутов"
    # CONFIGURATION = "Настройки"


def get_keyboard(commands: type(Enum)) -> List[KeyboardButton]:
    keyboard = []

    for command in commands:
        btn = KeyboardButton(command.value, callback_data=command.value)
        keyboard.append(btn)

    return keyboard


def get_markup() -> ReplyKeyboardMarkup:
    keyboards: List[KeyboardButton] = []
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=3)

    keyboards.extend(get_keyboard(BaseCommands))

    for btn in keyboards:
        markup.insert(btn)

    return markup


def generate_inline_markup(inlines: Generator) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup()
    for (key, value) in inlines:
        title = f"{value}"
        btn = InlineKeyboardButton(title, callback_data=str(key))
        inline_markup.add(btn)

    return inline_markup


def generate_configure_inline_markup() -> InlineKeyboardMarkup:
    return generate_inline_markup(ConfigureButtons.all())


def generate_configure_interval_markup() -> InlineKeyboardMarkup:
    markup = generate_inline_markup(ConfigureInterval.all())
    return add_back_button_to_markup(markup, callback_data='trip_interval_config')


def generate_trips_inline_markup(trip_params: List[LookingTripParams]) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup()

    for trip in trip_params:
        btn = InlineKeyboardButton(trip.title, callback_data=str(trip.id))
        inline_markup.add(btn)
    return inline_markup


def generate_trip_settings_inline_markup(trip: LookingTripParams) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup()

    btn_state = InlineKeyboardButton(
        trip.state.value,
        callback_data=TripConfigureType.STATE.value
    )
    inline_markup.add(btn_state)

    btn_interval = InlineKeyboardButton(
        f"{trip.interval} мин",
        callback_data=TripConfigureType.INTERVAL.value
    )
    inline_markup.insert(btn_interval)

    return add_back_button_to_markup(inline_markup, callback_data='configure_trip_back')


def change_markup_button_text_by_callback(markup: InlineKeyboardMarkup, callback: str, text: str):
    for row in markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == callback:
                btn.text = text


def add_back_button_to_markup(markup: InlineKeyboardMarkup, callback_data: str):
    if not markup:
        return markup

    btn_back = InlineKeyboardButton(
        "Назад",
        callback_data=callback_data
    )
    markup.add(btn_back)
    return markup


def add_button(markup, name: str, callback_data: str):
    if not markup or not isinstance(markup, InlineKeyboardMarkup):
        return markup

    btn = InlineKeyboardButton(
        name,
        callback_data=callback_data
    )
    markup.add(btn)
