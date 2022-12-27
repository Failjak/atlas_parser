import os
import time

import dotenv
from loguru import logger

from bot.main import run_bot
from parser import run_parser

dotenv.load_dotenv('.env')

if __name__ == "__main__":
    logger.info("Run Atlas Parser")
    run_bot()

    # interval = os.getenv("REQUEST_INTERVAL", 120)
    # url = os.getenv("URL")
    #
    # try:
    #     while True:
    #         run_parser(url, debug=os.getenv("DEBUG"), write_to_file=os.getenv("TO_FILE"))
    #         time.sleep(int(interval))
    # except KeyboardInterrupt:
    #     logger.info("Stop Atlas Parser")
