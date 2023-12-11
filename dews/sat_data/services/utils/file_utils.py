import base64
import logging
import os.path
from zipfile import ZipFile
import zipfile
import xmltodict

from dews.settings import EXTRACTED_FILES_PATH

logger = logging.getLogger("django")

class FileUtils:
    """
    Helps unzipping files, loads config yml file, decodes string, creates directories and many more.
    """
    logger = logging.getLogger("django")

    @staticmethod
    def extract_archive(source_path: str, mission: str) -> str|None:
        logging.debug(f"Extract archive method called. source_path='{source_path}', mission='{mission}'")

        folder_name, _ = os.path.splitext(os.path.basename(source_path))
        destination_path = os.path.join(EXTRACTED_FILES_PATH, mission)
        extracted_path = os.path.join(destination_path, folder_name)

        # Check if extracted archive exists
        if os.path.exists(extracted_path):
            logger.debug(f"Directory '{extracted_path}' exists.")
            return extracted_path

        # Extract archive
        try:
            with zipfile.ZipFile(source_path, "r") as archive_ref:
                logger.debug(f"Trying to extract archive. source_path='{source_path}', destination_path='{destination_path}', mission='{mission}'")
                archive_ref.extractall(destination_path)
        except Exception as e:
            logger.error(f"Failed to extract files from archive. source_path='{source_path}', mission='{mission}', error='{e}'")
            return None
        logger.info(f"Extracted archive from '{source_path}' to '{extracted_path}'.")

        # Check if extraction was successfull
        if os.path.exists(extracted_path):
            # Success
            logger.debug(f"Directory '{extracted_path}' exists.")
            return extracted_path
        else:
            # Fail
            logger.error(f"Directory at '{extracted_path}' does not exist.")
            return None

    @staticmethod
    def generate_path(*args):
        path = "/".join(map(str, args))
        return path.replace("//", "/")

    @staticmethod
    def xml_to_dict(metadata_path: str) -> dict:
        """
        Reads XML file which contains metadata about satellite images and returns a dictionary with all parsed information.
        """
        metadata_file = open(metadata_path, "r")
        metadata_dict = xmltodict.parse(metadata_file.read())
        metadata_file.close()

        if metadata_dict is False:
            logger.error(
                f"Could not read metadata file. metadata_path='{metadata_path}'")
        else:
            logger.debug(
                f"Reading metadata file has been read successfully. metadata_path='{metadata_path}'")

        return metadata_dict

    @staticmethod
    def get_dict_value_by_key(dictionary, searched_key):
        if isinstance(dictionary, dict):
            for key, value in dictionary.items():
                if key == searched_key:
                    return value
                result = FileUtils.get_dict_value_by_key(value, searched_key)
                if result is not None:
                    return result
        elif isinstance(dictionary, list):
            for item in dictionary:
                result = FileUtils.get_dict_value_by_key(item, searched_key)
                if result is not None:
                    return result
