import logging

from file_utils import FileUtils


class SIDLogger:
    LOG_FILE_LOCATION = "../app.log"  # default value (could be overwritten)
    CONFIGS = None
    DEBUG_STATUS = True  # default value (could be overwritten)

    def __init__(self):
        # Load config
        self.CONFIGS = FileUtils.load_config_yml()

        # Get log file location
        if len(self.CONFIGS["logger"]["log_file_location"]) > 0:
            # TODO: check if location exists
            self.LOG_FILE_LOCATION = self.CONFIGS["logger"]["log_file_location"]

        # Check which environment is used and set file mode
        if self.CONFIGS["environment"]["debug"]:
            self.DEBUG_STATUS = True
            filemode = "w"  # creates new log file on every run
        else:
            self.DEBUG_STATUS = False
            filemode = "a"  # appends log entries to log file

        # Set log level
        log_level = self.parse_log_level()

        # Set logger basic config
        logging.basicConfig(filename=f"{self.LOG_FILE_LOCATION}", filemode=filemode, encoding='utf-8',
                            format=self.CONFIGS["logger"]["log_format"],
                            datefmt=self.CONFIGS["logger"]["log_date_format"], level=log_level)

        logging.debug(f"Debug status = {self.DEBUG_STATUS}")

    def parse_log_level(self):
        match self.CONFIGS["logger"]["log_level"]:
            case "NOTSET":
                return logging.NOTSET
            case "DEBUG":
                return logging.DEBUG
            case _:
                return logging.WARNING

    def get_log_file_location(self):
        if len(self.LOG_FILE_LOCATION) == 0:
            logging.error("Log file location is empty. Please fix!")

        return self.LOG_FILE_LOCATION
