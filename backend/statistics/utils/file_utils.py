import base64
import logging
import os.path
from zipfile import ZipFile

import yaml
from backend.config import *


class FileUtils:
    """
    Helps unzipping files, loads config yml file, decodes string, creates directories and many more.
    """

    @staticmethod
    def unzip(zip_path, output_path):
        """
        Unzips a zip file which is located under `zip_path` to the destination `output_path`.
        :param zip_path:
        :param output_path:
        :return:
        """
        if output_path[-1] == "/":
            output_path = output_path[0:len(output_path) - 1]
            logging.warning(
                f"Output path ended with trailing slash! Trailing slash was removed. output_path='{output_path}'")

        if ".zip" in zip_path:
            logging.debug(f"'{zip_path}' is a valid zip archive.")
            # file name without ".zip" extension
            directory_name = zip_path[0:len(zip_path) - 4]
            # "/home/user/directory/test" -> "test"
            directory_name = directory_name.split("/")[-1]
            logging.debug(f"File name: '{directory_name}'")

            if os.path.isdir(f"{output_path}/{directory_name}"):
                logging.warning(
                    f"Directory already exists. Zip was not extracted. OUTPUT_PATH='{output_path}'")
                # TODO: update files, if directory already exists
                return f"{output_path}/{directory_name}"

            with ZipFile(zip_path) as zip_file:
                zip_file.extractall(output_path + "/" + directory_name)

            logging.debug(
                f"Zip file was successfully extracted. zip_path='{zip_path}', output_path='{output_path}'.")
        else:
            logging.error(
                f"Zip path does not include '.zip' extension. Please check, if file is a zip archive! zip_path='{zip_path}'")
            return ""  # exit

        return f"{output_path}/{directory_name}"

    @staticmethod
    def load_config_yml(config_yml_path: str = ""):
        # Set default config yml path if not provided
        if config_yml_path == "":
            config_yml_path = ROOT_PATH + "/config.yml"

        # Open config yml file
        with open(config_yml_path, 'r') as yml_file:
            logging.debug(
                f"Loaded config yml file. config_yml_path='{CONFIG_YML_PATH}'")
            return yaml.safe_load(yml_file)

    @staticmethod
    def get_debug_status() -> bool:
        return DEBUG_STATUS

    @staticmethod
    def get_root_path() -> str:
        return ROOT_PATH

    # Encoding + Decoding
    @staticmethod
    def decode_b64_string(b64_str: str):
        return base64.b64decode(b64_str).decode("utf-8")

    # Directories
    @staticmethod
    def create_file_directories():
        for path in FILES_PATH_LIST:
            if not os.exists(path):
                os.mkdir(path)
                logging.debug(f"Created directory '{path}'.")
            else:
                logging.debug(f"Directory '{path}' already exists.")
