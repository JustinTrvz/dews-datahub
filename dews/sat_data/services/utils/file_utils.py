import base64
import logging
import os.path
from zipfile import ZipFile
import zipfile
import xmltodict
import tarfile
import rasterio
from rasterio.enums import Resampling
import os


from dews.settings import EXTRACTED_FILES_PATH, MEDIA_ROOT

logger = logging.getLogger("django")


class FileUtils:
    """
    Helps unzipping files, loads config yml file, decodes string, creates directories and many more.
    """
    logger = logging.getLogger("django")

    @staticmethod
    def split_tiff(bands: list, tiff_path: str):
        """
        Extracts specified bands from a TIFF and saves each as a separate TIFF file.
        
        :param bands: A list of band names to extract (e.g., ["B02", "B03"]).
        :param tiff_path: Path to the source TIFF file.
        :return: A dictionary with band names as keys and paths to the new TIFF files as values.
        """
        output_tiff_files = {}
        
        with rasterio.open(tiff_path) as src:
            for i, band_name in enumerate(bands, start=1):
                band_name = band_name.lower()
                # Assuming the bands list directly corresponds to the band indices
                band_index = i  # Update this line if band_name to band_index mapping is needed
                band_data = src.read(band_index)

                # Define output file path
                output_tiff_path = os.path.join(os.path.dirname(tiff_path), f"{band_name}.tif")
                
                # Update the profile to reflect the single band
                profile = src.profile
                profile.update(count=1)
                
                # Write the band data to a new file
                with rasterio.open(output_tiff_path, 'w', **profile) as dst:
                    dst.write(band_data, 1)
                
                output_tiff_files[band_name] = output_tiff_path
        
        return output_tiff_files

    @staticmethod
    def extract_tar(tar_path, extract_path='.'):
        """
        Extracts a .tar file to the specified path.

        :param tar_path: The path to the .tar file to be extracted.
        :param extract_path: The directory to which the file should be extracted.
        """
        # Open the .tar file
        with tarfile.open(tar_path, 'r') as file:
            file.extractall(path=extract_path)
            logger.debug(f"Extracted '{tar_path}' to '{extract_path}'.")

        return extract_path

    @staticmethod
    def extract_archive(source_path: str, mission: str) -> str | None:
        logging.debug(
            f"Extract archive method called. source_path='{source_path}', mission='{mission}'")

        folder_name, _ = os.path.splitext(os.path.basename(source_path))
        destination_path = os.path.join(EXTRACTED_FILES_PATH, mission)
        extracted_path = os.path.join(destination_path, folder_name)

        # Check if extracted archive exists
        if os.path.exists(extracted_path):
            logger.debug(
                f"Extracted directory already exists. extracted_path='{extracted_path}'")
            return extracted_path

        # Extract archive
        try:
            with zipfile.ZipFile(source_path, "r") as archive_ref:
                logger.debug(
                    f"Trying to extract archive. source_path='{source_path}', destination_path='{destination_path}', mission='{mission}'")
                archive_ref.extractall(destination_path)
        except Exception as e:
            logger.error(
                f"Failed to extract files from archive. source_path='{source_path}', mission='{mission}', error='{e}'")
            return None
        logger.info(
            f"Extracted archive. source_path='{source_path}', extracted_path='{extracted_path}'.")

        # Check if extraction was successfull
        if os.path.exists(extracted_path):
            # Success
            logger.debug(
                f"Extraction was successfull. extracted_path='{extracted_path}'")
            return extracted_path
        else:
            # Fail
            logger.error(
                f"Extraction failed. extracted_path='{extracted_path}'")
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

    @staticmethod
    def get_all_dict_values_by_key(dictionary, searched_key):
        def recurse_find_values(curr_elem, key, found_values):
            if isinstance(curr_elem, dict):
                for k, v in curr_elem.items():
                    if k == key:
                        if isinstance(v, list):
                            found_values.extend(v)
                        else:
                            found_values.append(v)
                    else:
                        recurse_find_values(v, key, found_values)
            elif isinstance(curr_elem, list):
                for item in curr_elem:
                    recurse_find_values(item, key, found_values)

        values = []
        recurse_find_values(dictionary, searched_key, values)
        return values