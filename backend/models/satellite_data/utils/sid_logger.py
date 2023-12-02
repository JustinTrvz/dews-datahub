import logging

from backend.config import *


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

        # Create a FileHandler in append mode
        file_handler = logging.FileHandler(LOGGER_FILE_LOCATION, mode='a')
        file_handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=LOGGER_DATE_FORMAT))

        # Add the FileHandler to the logger
        logging.getLogger().addHandler(file_handler)

        logging.debug(f"Debug='{DEBUG_STATUS}'")

    def get_log_file_location(self):
        if len(LOGGER_FILE_LOCATION) == 0:
            logging.error("Log file location is empty. Please fix!")

        return LOGGER_FILE_LOCATION
