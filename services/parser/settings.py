import os

from pydantic import BaseSettings


class ParserSettings(BaseSettings):
    url: str


if os.environ.get("IS_HEROKU", None):
    parser_settings = ParserSettings(
        url=os.environ.get("URL")
    )
else:
    parser_settings = ParserSettings(_env_file='.env')
