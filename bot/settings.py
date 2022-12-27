import os

from aiogram_datepicker import DatepickerSettings
from pydantic import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str


def _get_datepicker_settings():
    return DatepickerSettings()


if os.environ.get("IS_HEROKU", None):
    bot_settings = BotSettings(
        bot_token=os.environ.get('BOT_TOKEN'),
    )
else:
    bot_settings = BotSettings(_env_file='.env')
