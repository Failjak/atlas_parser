import dotenv
from loguru import logger

from bot.main import run_bot

dotenv.load_dotenv('.env')

if __name__ == "__main__":
    logger.level("PARSER", no=38, color="<yellow>", icon="🐍")
    logger.level("BOT", no=38, color="<red>", icon="🐍")
    run_bot()
