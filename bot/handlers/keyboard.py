from enum import Enum
from typing import List, Generator

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot.constants import ConfigureButtons, ConfigureInterval
from services.atlas.dto import LookingTripParams


class BaseCommands(Enum):
    CHOOSE_TRIP = "Выбрать маршрут"
    ADD_TRIP = "Добавить маршрут"
    STOP_LOOKING = "Остановить поиск"
    CONFIGURATION = "Настройки"


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


def generate_configure_interval_markup(**kwargs) -> InlineKeyboardMarkup:
    return generate_inline_markup(ConfigureInterval.all())


def generate_trip_params_inline_markup(trip_params: List[LookingTripParams]) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup()

    for trip in trip_params:
        title = f"{trip.full_path}"
        btn = InlineKeyboardButton(title, callback_data=trip.full_path)
        inline_markup.add(btn)

        btn_state = InlineKeyboardButton(trip.state.value, callback_data=str(trip.id))
        inline_markup.insert(btn_state)

    return inline_markup


def change_markup_button_text_by_callback(markup: InlineKeyboardMarkup, callback: str, text: str):
    for row in markup.inline_keyboard:
        for btn in row:
            if btn.callback_data == callback:
                btn.text = text


configure_button_to_markups = {
    ConfigureButtons.INTERVAL.name: generate_configure_interval_markup
}
