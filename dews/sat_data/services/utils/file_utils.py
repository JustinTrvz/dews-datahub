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
    def xml_to_dict(xml_path: str) -> dict:
        """
        Reads XML file and transforms it into a dictionary.
        """
        try:
            logger.debug(f"Opening xml file. xml_path='{xml_path}'")
            xml_file = open(xml_path, "r")
        except Exception as e:
            logger.error(
                f"Failed to read xml file. xml_path='{xml_path}', error='{e}'")
            return False
        
        logger.debug(f"Parsing xml file. xml_path='{xml_path}'")
        xml_dict = xmltodict.parse(xml_file.read())
        logger.debug(f"Closing xml file. xml_path='{xml_path}'")
        xml_file.close()

        if xml_dict is False:
            logger.error(
                f"Failed to read xml file. xml_path='{xml_path}'")
        else:
            logger.debug(
                f"Successfully read xml file. xml_path='{xml_path}'")

        return xml_dict

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
        return None
