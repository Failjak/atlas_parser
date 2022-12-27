import os

from pydantic import BaseSettings


class BotSettings(BaseSettings):
    bot_token: str


if os.environ.get("IS_HEROKU", None):
    bot_settings = BotSettings(
        bot_token=os.environ.get('BOT_TOKEN'),
    )
else:
    bot_settings = BotSettings(_env_file='.env')
