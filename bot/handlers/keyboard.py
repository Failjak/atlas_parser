from enum import Enum
from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot.constants import ConfigureButtons, ConfigureInterval


class BaseCommands(Enum):
    CHOOSE_TRIP = "Choose trip"
    STOP_LOOKING = "Stop looking"
    CONFIGURATION = "Configurate"


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


def generate_inline_markup(inlines: type(Enum)) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup()
    for _enum in inlines:
        title = f"{_enum.value}"
        btn = InlineKeyboardButton(title, callback_data=_enum.name)
        inline_markup.add(btn)

    return inline_markup


def generate_configure_inline_markup(is_run: bool) -> InlineKeyboardMarkup:
    inline_markup = generate_inline_markup(ConfigureButtons)
    btn = InlineKeyboardButton(f"Поиск билетов - {is_run}", callback_data="IS_RUNNING")
    inline_markup.add(btn)
    return inline_markup


def generate_configure_interval_markup(**kwargs) -> InlineKeyboardMarkup:
    return generate_inline_markup(ConfigureInterval)


configure_button_to_markups = {
    ConfigureButtons.INTERVAL.name: generate_configure_interval_markup
}
