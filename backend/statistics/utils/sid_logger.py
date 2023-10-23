import logging

from statistics.utils.file_utils import FileUtils
from config import *


class SidLogger:
    def __init__(self):
        # Set logger basic config
        logging.basicConfig(filename=LOGGER_FILE_LOCATION,
                            filemode=LOGGER_FILE_MODE,
                            encoding='utf-8',
                            format=LOGGER_FORMAT,
                            datefmt=LOGGER_DATE_FORMAT,
                            level=LOGGER_LEVEL
                            )

        logging.debug(f"Debug='{DEBUG_STATUS}'")

    def get_log_file_location(self):
        if len(LOGGER_FILE_LOCATION) == 0:
            logging.error("Log file location is empty. Please fix!")

        return LOGGER_FILE_LOCATION
