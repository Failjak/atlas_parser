import dotenv
from loguru import logger

from bot.main import run_bot

dotenv.load_dotenv('.env')

if __name__ == "__main__":
    logger.info("Run Atlas Parser")
    run_bot()
