import datetime
import logging

import xmltodict
import uuid
from backend.data.database.firebase import FirebaseDatabase, FirebaseStorage
from backend.data.models.satellite_data.satellite_types import SatelliteTypes

from backend.statistics.utils.file_utils import FileUtils
from backend.statistics.metrics_calculator import MetricsCalculator
from backend.config import *

"""
Satellite image data object specialized for S2B MSIL2A (Sentinel-2B) satellite image data.
"""


class ImageTypes:
    '''Image types for every index (e.g. NDVI) used and additionally the RGB image.'''
    RGB = "rgb"
    NDVI = "ndvi"
    WATER = "water"
    NDWI = "ndwi"


class Sentinel2BData:
    # Basic capture information
    ID = ""
    USER_ID = ""
    AREA_NAME = ""
    CITY = ""
    COUNTRY = ""
    POSTAL_CODE = 0
    CREATION_TIME = datetime.datetime.now()
    RGB_IMG_PATH_LOCAL = ""
    RGB_IMG_PATH_STORAGE = ""

    # Basic file information
    METADATA_FILE_NAME = ""
    INSPIRE_FILE_NAME = ""
    ROOT_PATH = ""
    DIRECTORY_PATH_LOCAL = ""
    DIRECTORY_PATH_STORAGE = ""
    GRANULE_PATH = ""
    IMG_SAVE_PATH_LOCAL = ""
    IMG_SAVE_PATH_STORAGE = ""
    FILE_SAVE_LOCATION = ""

    # Information about captured satellite image
    PRODUCT_START_TIME = ""
    PRODUCT_STOP_TIME = ""
    PROCESSING_LEVEL = ""
    PRODUCT_TYPE = ""
    PROCESSING_BASELINE = ""
    PRODUCT_DOI = ""
    GENERATION_TIME = ""

    # Calculated indexes
    # NDVI
    NDVI = -1.0
    NDVI_IMG_PATH_LOCAL = ""
    NDVI_IMG_PATH_STORAGE = ""
    NDVI_CALC_TIME = None
    # MOISTURE INDEX
    MOISTURE = -1.0
    MOISTURE_IMG_PATH_LOCAL = ""
    MOISTURE_IMG_PATH_STORAGE = ""
    MOISTURE_CALC_TIME = None

    # Geographic bounding box
    WEST_BOUND_LONGITUDE = None
    EAST_BOUND_LONGITUDE = None
    SOUTH_BOUND_LATITUDE = None
    NORTH_BOUND_LATITUDE = None
    geographic_bounding_box = {
        "north": -1.0,
        "east": -1.0,
        "south": -1.0,
        "west": -1.0,
    }

    # R10m
    r10m_img_path = ""
    r10m_vars = {
        "R10m_AOT": None,
        "R10m_B02": None,
        "R10m_B03": None,
        "R10m_B04": None,
        "R10m_B08": None,
    }

    # R20m
    r20m_img_path = ""
    r20m_vars = {
        "R20m_AOT": None,
        "R20m_B01": None,
        "R20m_B02": None,
        "R20m_B03": None,
        "R20m_B04": None,
        "R20m_B05": None,
        "R20m_B06": None,
        "R20m_B07": None,
        "R20m_B8A": None,
        "R20m_B11": None,
        "R20m_B12": None,
        "R20m_SCL": None,
        "R20m_TCI": None,
        "R20m_WVP": None,
    }

    # R60m
    r60m_img_path = ""
    r60m_vars = {
        "R60m_AOT": None,
        "R60m_B01": None,
        "R60m_B02": None,
        "R60m_B03": None,
        "R60m_B04": None,
        "R60m_B05": None,
        "R60m_B06": None,
        "R60m_B07": None,
        "R60m_B8A": None,
        "R60m_B09": None,
        "R60m_B11": None,
        "R60m_B12": None,
        "R60m_SCL": None,
        "R60m_TCI": None,
        "R60m_WVP": None,
    }

    def __init__(self, directory_path_local: str, user_id: str = "Unknown", img_save_location: str = "",
                 file_save_location: str = "", area_name: str = "Unknown", country: str = "Unknown",
                 city: str = "Unknown", postal_code: int = 0, generate_imgs: bool = True):
        """
        A satellite image data object contains information about the capturing, indexes, image files and many more.

        :param directory_path: File path to the directory (e.g. extracted files from zip).
        :param user_id: ID of the owner of the area of the satellite image.
        :param img_save_location: Location where the index images should be stored.
        :param area_name: Name of the area.
        :param country: Country name of the area.
        :param city: City name of the area.
        :param postal_code: Postal code of the area.
        """
        # Basic information
        self.ID = str(uuid.uuid4())  # Creates and sets ID
        self.USER_ID = user_id  # set user/owner ID
        # Location information
        self.AREA_NAME = area_name
        self.COUNTRY = country
        self.CITY = city
        self.POSTAL_CODE = postal_code
        # Directory path
        self.DIRECTORY_PATH_LOCAL = directory_path_local
        # Other information
        self.METADATA_FILE_NAME = FileUtils.generate_path(
            self.DIRECTORY_PATH_LOCAL, S2B_METADATA_FILE_NAME)
        self.INSPIRE_FILE_NAME = FileUtils.generate_path(
            self.DIRECTORY_PATH_LOCAL, S2B_INSPIRE_FILE_NAME)
        # Set directory name by extraction from zip path
        self.__set_directory_name(directory_path_local)

        # Check if naming convention is met
        if self.DIRECTORY_PATH_LOCAL.count("_") != 6:
            logging.error(
                f"Directory name contains character '/' only {self.DIRECTORY_PATH_LOCAL.count('_')} times, but needs to have ")
            logging.error(
                f"Directory name does not meet naming convention requirements. DIRECTORY_NAME='{self.DIRECTORY_PATH_LOCAL}'"
                "See https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/naming"
                "-convention for more information.")
            return  # exit program

        # Sets information about captured satellite image
        self.__set_satellite_img_information()

        # Set save locations
        if len(img_save_location) > 0:
            self.IMG_SAVE_PATH_LOCAL = img_save_location
        else:
            self.IMG_SAVE_PATH_LOCAL = IMAGES_FILES_PATH

        if len(file_save_location) > 0:
            self.FILE_SAVE_LOCATION = file_save_location
        else:
            self.FILE_SAVE_LOCATION = OTHER_FILES_PATH

        # Object can be created without calculation. Be aware: no images can be shown!
        if generate_imgs:
            ok = self.generate_imgs()
            if ok <= 0:
                logging.error(f"Failed to generate images. error='{ok}'")
                return

        # Set coordinates
        self.set_coordinates()

        # Check if everything is set correctly
        valid = self.is_valid()
        if valid >= 1:
            ok = self.upload()
            if ok <= 0:
                logging.error(
                    f"Failed to upload data and files of satellite image data object. error='{ok}', id='{self.ID}'")
                return
            else:
                logging.debug(
                    f"Successfully uploaded data and files ot of satellite image data object. id='{self.ID}'")
                self.createNotification()
                return
        else:
            logging.error(
                f"Satellite image data object is not valid! error='{valid}', id='{self.ID}'")
            return
        
    def createNotification(self):
        data = {
           "id": str(uuid.uuid4()),
           "userId": self.USER_ID,
           "category": "Calculation",
           "message": f"Calculation done for satellite image data '{self.ID}'",
           "thumbnailStoragePath": self.RGB_IMG_PATH_STORAGE,
        }
        ok = FirebaseDatabase.set_entry(
            f"notifications/{self.USER_ID}", data)
        if not ok:
            logging.error(f"Could not set notification. self.USER_ID='{self.USER_ID}', self.ID='{self.ID}'")


    @staticmethod
    def init_from_json(json_data):
        return Sentinel2BData(
            directory_path_local=json_data["directory_path_local"],
            user_id=json_data["user_id"],
            area_name=json_data["area_name"],
            city=json_data["city"],
            postal_code=json_data["postal_code"],
            country=json_data["country"],
        )

    def generate_imgs(self) -> int:
        try:
            # Create RGB-image
            logging.debug(
                f"Starting RGB (image generation. id='{self.ID}', satellite_type='{SatelliteTypes.SENTINEL_2B.lower()}'")
            self.create_rgb_img()
            # Calculate indexes
            # NDVI
            logging.debug(
                f"Starting NDVI image generation. id='{self.ID}', satellite_type='{SatelliteTypes.SENTINEL_2B.lower()}'")
            self.calculate_ndvi()
            # Water
            logging.debug(
                f"Starting water image generation. id='{self.ID}', satellite_type='{SatelliteTypes.SENTINEL_2B.lower()}'")
            self.calculate_moisture()
        except Exception as e:
            logging.error(
                f"Failed to generate images. id='{self.ID}', satellite_type='{SatelliteTypes.SENTINEL_2B.lower()}'")
            return -1

        return 1

    def upload(self) -> int:
        # Upload files
        self.RGB_IMG_PATH_STORAGE = self.upload_image(ImageTypes.RGB)  # RGB
        self.NDVI_IMG_PATH_STORAGE = self.upload_image(ImageTypes.NDVI)  # NDVI
        self.MOISTURE_IMG_PATH_STORAGE = self.upload_image(
            ImageTypes.WATER)  # Water content
        logging.debug(f"Upload to storage complete. id='{self.ID}'")

        # Write to database
        db_ref = os.path.join(
            "sid", SatelliteTypes.SENTINEL_2B.lower(), self.ID)
        self.DIRECTORY_PATH_STORAGE = db_ref
        self.IMG_SAVE_PATH_STORAGE = os.path.join(db_ref, "images")

        data_dict = self.to_dict()
        ok = FirebaseDatabase.set_entry(db_ref, data_dict)
        if ok <= 0:
            logging.error(
                f"Failed to set entry for satellte image data object in database. error='{ok}', id='{self.ID}', db_ref='{db_ref}'")
            return -1

        logging.debug(
            f"Write to database complete. id='{self.ID}', db_ref='{db_ref}'")
        return 1

    def upload_image(self, img_type: str):
        '''
        Uploads generated (index) image to storage.

        Use ImageTypes' constants as input for `img_type`. For example `upload_image(ImageTypes.NDVI, "test/image.png")`.
        '''
        if img_type == ImageTypes.RGB:
            local_path = self.RGB_IMG_PATH_LOCAL
        elif img_type == ImageTypes.NDVI:
            local_path = self.NDVI_IMG_PATH_LOCAL
        elif img_type == ImageTypes.WATER:
            local_path = self.MOISTURE_IMG_PATH_LOCAL

        directory_path = os.path.join(
            "sid",  SatelliteTypes.SENTINEL_2B.lower(), self.ID, "images", img_type)
        storage_path = FirebaseStorage.upload_file(directory_path, local_path)
        if storage_path == "":
            logging.error(f"Failed to upload file. directory_path='{directory_path}', local_path='{local_path}'")
        else:
            logging.debug(
            f"Uploaded {img_type} image to storage. self.ID='{self.ID}', directory_path='{directory_path}', {img_type}_img_path_local='{local_path}'")

        return storage_path

    def __set_directory_name(self, zip_path: str):
        """
        Extracts directory name from zip path.
        """
        self.DIRECTORY_PATH_LOCAL = zip_path[zip_path.rfind("/"):]
        logging.debug(
            f"Directory name has been set. DIRECTORY_NAME='{self.DIRECTORY_PATH_LOCAL}'.")

    def read_metadata_xml(self, metadata_path: str):
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

    def set_basic_granule_path(self, img_data_path: str):
        split_img_data_path = img_data_path.split("/")
        subdir = split_img_data_path[-4]
        # e.g. [... , 'L2A_T32UNE_A033353_20230726T103642', 'IMG_DATA', 'R20m', 'T32UNE_20230726T103629_AOT_20m.jp2']]
        self.GRANULE_PATH = os.path.join(
            self.DIRECTORY_PATH_LOCAL, "GRANULE", subdir)
        logging.debug(
            f"Set granule path. id='{self.ID}', GRANULE_PATH='{self.GRANULE_PATH}'.")

    def set_granule_img_data_paths(self, granule_img_data_paths):
        """
        Sets all path to the granule image data directories for the range 10m, 20m and 60m.
        """

        variable_mapping = {
            "10m": self.r10m_vars,
            "20m": self.r20m_vars,
            "60m": self.r60m_vars,
        }

        for img_data_path in granule_img_data_paths:
            range_meters = img_data_path[-3:]  # "...B02_10m" -> "10m"
            frequency_band = img_data_path[-7:-4]  # "...B02_10m" -> "B02"

            if self.GRANULE_PATH == "":
                self.set_basic_granule_path(img_data_path)

            path = FileUtils.generate_path(EXTRACTED_FILES_PATH, SatelliteTypes.SENTINEL_2B.lower(
            ), self.DIRECTORY_PATH_LOCAL, img_data_path + S2B_IMG_FILE_EXTENSION)
            if range_meters in variable_mapping:
                variable_mapping[range_meters][f"R{range_meters}_{frequency_band}"] = path

    def __set_satellite_img_information(self):
        """
        Gets and sets information read from a metadata XML file.
        """
        metadata_dict = self.read_metadata_xml(
            self.METADATA_FILE_NAME)  # reading metadata XML file "MTD_MSIL2A.xml"

        # get and set paths to satellite image data
        granule_img_data_paths = \
            metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"]["Product_Organisation"][
                "Granule_List"]["Granule"]["IMAGE_FILE"]
        self.set_granule_img_data_paths(granule_img_data_paths)

        # basic product information
        self.PRODUCT_START_TIME = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"][
            "PRODUCT_START_TIME"]
        self.PRODUCT_STOP_TIME = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"][
            "PRODUCT_STOP_TIME"]
        self.PROCESSING_LEVEL = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"][
            "PROCESSING_LEVEL"]
        self.PRODUCT_TYPE = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"]["PRODUCT_TYPE"]
        self.PROCESSING_BASELINE = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"][
            "PROCESSING_BASELINE"]
        self.PRODUCT_DOI = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"]["PRODUCT_DOI"]
        self.GENERATION_TIME = metadata_dict["n1:Level-2A_User_Product"]["n1:General_Info"]["Product_Info"][
            "GENERATION_TIME"]

        logging.debug(f"Set satellite image information. id='{self.ID}'")

    def get_directory_path(self):
        """
        Returns local directory path and storage directory path as tuple.

        Return value: (self.DIRECTORY_PATH_LOCAL, self.DIRECTORY_PATH_STORAGE)
        """
        return self.DIRECTORY_PATH_LOCAL, self.DIRECTORY_PATH_STORAGE

    def set_coordinates(self):
        """
        Parses coordinates from metadata file and set coordinates variables of this class.
        """
        inspire_dict = self.read_metadata_xml(self.INSPIRE_FILE_NAME)
        geograpic_bounding_box = \
            inspire_dict["gmd:MD_Metadata"]["gmd:identificationInfo"]["gmd:MD_DataIdentification"]["gmd:extent"][
                "gmd:EX_Extent"]["gmd:geographicElement"]["gmd:EX_GeographicBoundingBox"]

        self.NORTH_BOUND_LATITUDE = float(
            geograpic_bounding_box["gmd:northBoundLatitude"]["gco:Decimal"])
        self.EAST_BOUND_LONGITUDE = float(
            geograpic_bounding_box["gmd:eastBoundLongitude"]["gco:Decimal"])
        self.SOUTH_BOUND_LATITUDE = float(
            geograpic_bounding_box["gmd:southBoundLatitude"]["gco:Decimal"])
        self.WEST_BOUND_LONGITUDE = float(
            geograpic_bounding_box["gmd:westBoundLongitude"]["gco:Decimal"])

        self.geographic_bounding_box["north"] = self.NORTH_BOUND_LATITUDE
        self.geographic_bounding_box["east"] = self.EAST_BOUND_LONGITUDE
        self.geographic_bounding_box["south"] = self.SOUTH_BOUND_LATITUDE
        self.geographic_bounding_box["west"] = self.WEST_BOUND_LONGITUDE

    def get_coordinates(self):
        # TODO: return coordinates
        print("TODO")
        return 0

    def is_valid(self) -> int:
        # Check coordinates
        logging.debug(f"Checking coordinates. id='{self.ID}'")
        ok_coordinates = self.__check_coordinates()
        if ok_coordinates != 1:
            logging.error(
                f"Error occured while checking coordinates! error={ok_coordinates}, id='{self.ID}'")
            return -1  # TODO: error code
        else:
            logging.debug(f"Coordinates are complete. id='{self.ID}'")

        # Check file paths
        logging.debug(f"Checking file paths. id='{self.ID}'")
        ok_paths = self.__check_file_paths()
        if ok_paths != 1:
            logging.error(
                f"Error occured while checking file paths! error={ok_paths}, id='{self.ID}'")
            return -1
        else:
            logging.debug(f"File paths are complete. id='{self.ID}'")

        # Check image generation
        logging.debug(f"Checking if image generation. id='{self.ID}'")
        ok_imgs = self.__check_imgs()
        if ok_imgs != 1:
            logging.error(
                f"Error occured while checking images! error={ok_paths}, id='{self.ID}'")
            return -1  # TODO: error code

        return 1  # object is valid

    def __check_imgs(self) -> int:
        empty_paths = []
        if self.NDVI_IMG_PATH_LOCAL == "":
            empty_paths.append("NDVI")
        if self.MOISTURE_IMG_PATH_LOCAL == "":
            empty_paths.append("Moisture")
        if self.RGB_IMG_PATH_LOCAL == "":
            empty_paths.append("RGB")

        if len(empty_paths) >= 1:
            logging.error(
                f"Image paths for {empty_paths} are empty. id='{self.ID}'")
            return -1
        else:
            logging.debug(f"Image paths are complete. id='{self.ID}'")
            return 1

    def __check_coordinates(self) -> int:
        if (self.NORTH_BOUND_LATITUDE == -1.0) and (self.EAST_BOUND_LONGITUDE == -1.0) and (
                self.SOUTH_BOUND_LATITUDE == -1.0) and (self.WEST_BOUND_LONGITUDE == -1.0):
            logging.error(
                f"Coordinates have not been set correctly! id='{self.ID}'")
            return -1  # TODO: error code

        if self.NORTH_BOUND_LATITUDE == -1.0:
            logging.warning(
                f"North bound latitude has still the default value. id='{self.ID}', NORTH_BOUND_LATITUDE='{self.NORTH_BOUND_LATITUDE}'")

        if self.EAST_BOUND_LONGITUDE == -1.0:
            logging.warning(
                f"East bound longitude has still the default value. id='{self.ID}', EAST_BOUND_LONGITUDE='{self.EAST_BOUND_LONGITUDE}'")

        if self.SOUTH_BOUND_LATITUDE == -1.0:
            logging.warning(
                f"South bound latitude has still the default value. id='{self.ID}', SOUTH_BOUND_LATITUDE='{self.SOUTH_BOUND_LATITUDE}'")

        if self.WEST_BOUND_LONGITUDE == -1.0:
            logging.warning(
                f"West bound longitude has still the default value. id='{self.ID}', WEST_BOUND_LONGITUDE='{self.WEST_BOUND_LONGITUDE}'")

        return 1

    def __check_file_paths(self) -> int:
        """
         Checks if any needed path to a satellite image file is missing.
         """

        # merge all dictionaries
        all_variables = self.r10m_vars | self.r20m_vars | self.r60m_vars

        missing_value = False
        for key in all_variables:
            if (all_variables[key] is None) or (all_variables[key] == ""):
                missing_value = True
                logging.warning(
                    f"Attribute has no value. id='{self.ID}', key='{key}'")

        if missing_value is False:
            logging.debug(
                f"All attributes for range 10m, 20m and 60m are complete. id='{self.ID}'")
            return 1
        else:
            return -1  # TODO: error code

    def create_rgb_img(self) -> str:
        rgb_img_path = MetricsCalculator.create_rgb_img(
            sid_id=self.ID,
            red_band_04=self.r20m_vars["R20m_B04"],
            green_band_03=self.r20m_vars["R20m_B03"],
            blue_band_02=self.r20m_vars["R20m_B02"],
            save_location=IMAGES_FILES_PATH,
        )
        logging.debug(
            f"Merged red, green and blue bands and created image. rgb_img_path='{rgb_img_path}'")

        self.RGB_IMG_PATH_LOCAL = rgb_img_path
        return rgb_img_path

    def calculate_ndvi(self):
        ndvi_img_path = MetricsCalculator.calculate_ndvi(
            sid_id=self.ID,
            image_path_04=self.r10m_vars["R10m_B04"],
            image_path_08=self.r10m_vars["R10m_B08"],
            save_location=self.IMG_SAVE_PATH_LOCAL,
        )
        logging.debug(
            f"Set NDVI image path. ndvi_img_path='{ndvi_img_path}'")
        current_datetime = datetime.datetime.now()
        self.NDVI_CALC_TIME = current_datetime
        logging.debug(
            f"Calculated NDVI for SatelliteImageData. id='{self.ID}'.")

        self.NDVI_IMG_PATH_LOCAL = ndvi_img_path
        return ndvi_img_path

    def calculate_moisture(self):
        water_img_path = MetricsCalculator.calculate_moisture(
            sid_id=self.ID,
            image_path_8a=self.r20m_vars["R20m_B8A"],
            image_path_11=self.r20m_vars["R20m_B12"],
            save_location=self.IMG_SAVE_PATH_LOCAL,
        )
        current_datetime = datetime.datetime.now()
        self.MOISTURE_CALC_TIME = current_datetime

        logging.debug(
            f"Calculated water content for SatelliteImageData. id='{self.ID}', local_path='{water_img_path}'")

        self.MOISTURE_IMG_PATH_LOCAL = water_img_path
        return water_img_path

    def to_dict(self):
        return {
            "basic": {
                "id": self.ID,
                "user_id": self.USER_ID,
                "area_name": self.AREA_NAME,
                "country": self.COUNTRY,
                "city": self.CITY,
                "postal_code": self.POSTAL_CODE,
                "creation_time": self.CREATION_TIME.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "satellite_type": SatelliteTypes.SENTINEL_2B,
            },

            "images": {
                "rgb": {
                    "img_path_storage": self.RGB_IMG_PATH_STORAGE,
                    "img_path_local": self.RGB_IMG_PATH_LOCAL,
                    "archived_img_paths": [],
                },
                "indexes": {
                    "ndvi": {
                        "value": self.NDVI,
                        "img_path_storage": self.NDVI_IMG_PATH_STORAGE,
                        "img_path_local": self.NDVI_IMG_PATH_LOCAL,
                        "calc_time": self.NDVI_CALC_TIME.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "archived_img_paths": [],
                    },
                    "moisture": {
                        "value": self.MOISTURE,
                        "img_path_storage": self.MOISTURE_IMG_PATH_STORAGE,
                        "img_path_local": self.MOISTURE_IMG_PATH_LOCAL,
                        "calc_time": self.MOISTURE_CALC_TIME.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        "archived_img_paths": [],
                    }
                },
            },

            "bound_latitudes": {
                "north": self.NORTH_BOUND_LATITUDE,
                "east": self.EAST_BOUND_LONGITUDE,
                "south": self.SOUTH_BOUND_LATITUDE,
                "west": self.WEST_BOUND_LONGITUDE,
            },

            "file_paths": {
                "granule_path": self.GRANULE_PATH,
                "directory_path_local": self.DIRECTORY_PATH_LOCAL,
                "directory_path_storage": self.DIRECTORY_PATH_STORAGE,
                "img_save_path_local": self.IMG_SAVE_PATH_LOCAL,
                "img_save_path_storage": self.IMG_SAVE_PATH_STORAGE,

            },

            "capture_information": {
                "product_start_time": self.PRODUCT_START_TIME,
                "product_stop_time": self.PRODUCT_STOP_TIME,
                "processing_level": self.PROCESSING_LEVEL,
                "product_type": self.PRODUCT_TYPE,
                "generation_time": self.GENERATION_TIME,
            },
        }

    def get_id(self):
        return self.ID
