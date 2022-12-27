from enum import Enum
from typing import List

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


class BaseCommands(Enum):
    CHOOSE_TRIP = 'Choose trip'
    STOP_LOOKING = 'Stop looking'


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


def generate_inline_markup(workplaces: dict) -> InlineKeyboardMarkup:
    inline_markup = InlineKeyboardMarkup()
    for name, accounts in workplaces.items():
        title = f'{name} - {accounts}'
        btn = InlineKeyboardButton(title, callback_data=name)
        inline_markup.add(btn)

    return inline_markup