import base64
import logging
import os.path
from zipfile import ZipFile
import zipfile
import xmltodict


from backend.config import *


class FileUtils:
    """
    Helps unzipping files, loads config yml file, decodes string, creates directories and many more.
    """

    @staticmethod
    def extract_file_name(path: str):
        return os.path.basename(path)

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
    def get_debug_status() -> bool:
        return DEBUG_STATUS

    @staticmethod
    def get_root_path() -> str:
        return ROOT_PATH

    # Directories
    @staticmethod
    def create_file_directories():
        for path in FILES_PATH_LIST:
            if not os.path.exists(path):
                os.mkdir(path)
                logging.debug(f"Created directory '{path}'.")
            else:
                logging.debug(f"Directory '{path}' already exists.")

    @staticmethod
    def generate_path(*args):
        path = "/".join(args)
        return path.replace("//", "/")
    
    @staticmethod
    def extract_zip(zip_path: str):
        # Get the directory containing the zip file
        zip_dir = os.path.dirname(zip_path)

        # Open the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Determine the extraction path (use the zip file's name without extension)
            zip_base_name = os.path.splitext(os.path.basename(zip_path))[0]
            extraction_path = os.path.join(zip_dir, zip_base_name)

            # Extract the contents of the zip file to the extraction path
            zip_ref.extractall(extraction_path)

        return extraction_path
    
    @staticmethod
    def xml_to_dict(metadata_path: str) -> dict:
        """
        Reads XML file which contains metadata about satellite images and returns a dictionary with all parsed information.
        """
        metadata_file = open(metadata_path, "r")
        metadata_dict = xmltodict.parse(metadata_file.read())
        metadata_file.close()

        if metadata_dict is False:
            logging.error(
                f"Could not read metadata file. metadata_path='{metadata_path}'")
        else:
            logging.debug(
                f"Reading metadata file has been read successfully. metadata_path='{metadata_path}'")

        return metadata_dict