import logging
from models.satellite_data.satellite_mission import SatelliteMission
from database.firebase import FirebaseStorage
from models.satellite_data.statistics.metrics_calculator import MetricsCalculator
from models.satellite_data.utils.file_utils import FileUtils

from models.init_vars import InitVar
from models.satellite_data.satellite_product_type import Sentinel1AProductType
from models.satellite_data.satellite_data import SatelliteData
from config import *


class Sentinel1AData(SatelliteData):
    """ Sentinel1AData inherits from SatelliteData"""
    # Files and directories paths
    # Measurment directory
    MEASURMENT_PATH_STORAGE = InitVar.UNKNOWN.value  # contains .tiff files
    MEASURMENT_PATH_LOCAL = InitVar.UNKNOWN.value
    # Manifest file
    MANIFEST_PATH_STORAGE = InitVar.UNKNOWN.value  # contains meta data
    MANIFEST_PATH_LOCAL = InitVar.UNKNOWN.value
    MANIFEST_DICT = {}

    # TIFF Image paths
    BANDS_TIFF_PATHS_LOCAL = {
        "B01": InitVar.EMPTY.value,
        "B02": InitVar.EMPTY.value,
        "B03": InitVar.EMPTY.value,
        "B04": InitVar.EMPTY.value,
        "B05": InitVar.EMPTY.value,
        "B06": InitVar.EMPTY.value,
    }
    BANDS_TIFF_PATHS_STORAGE = {
        "B01": InitVar.EMPTY.value,
        "B02": InitVar.EMPTY.value,
        "B03": InitVar.EMPTY.value,
        "B04": InitVar.EMPTY.value,
        "B05": InitVar.EMPTY.value,
        "B06": InitVar.EMPTY.value,
    }

    # Generated images paths
    RGB_IMG_PATH_LOCAL = InitVar.EMPTY.value
    RGB_IMG_PATH_STORAGE = InitVar.EMPTY.value

    def __init__(self, directory_path_local: str,
                 user_id: str,
                 area_name: str = InitVar.UNKNOWN.value,
                 city: str = InitVar.UNKNOWN.value,
                 country: str = InitVar.UNKNOWN.value,
                 postal_code: int = InitVar.MINUS_INT.value,
                 product_type: str = Sentinel1AProductType.UNKNOWN.value) -> None:
        # Init from parent class
        super().__init__(directory_path_local,
                         user_id,
                         area_name,
                         SatelliteMission.SENTINEL_1A.value,
                         city,
                         country,
                         postal_code)
        # Mission specific attributes
        self.SATELLITE_PRODUCT_TYPE = product_type
        # Manifest file
        self.MANIFEST_PATH_LOCAL = FileUtils.generate_path(
            self.DIRECTORY_PATH_LOCAL, S1A_MANIFEST_FILE_NAME)
        self.MANIFEST_PATH_STORAGE = FileUtils.generate_path(
            self.DIRECTORY_PATH_STORAGE, S1A_MANIFEST_FILE_NAME)
        self.MANIFEST_DICT = FileUtils.xml_to_dict(self.MANIFEST_PATH_LOCAL)
        # Functions that set attributes
        self.__set_thumbnail_path()
        self.__set_coordinates()
        self.__set_time_info()
        self.__set_bands_paths()
        # Generations, calculations, uploads, etc.
        self.__generate_rgb()
        self.__upload_files()
        # Debug log
        logging.debug(
            f"Finished creating Sentinel1AData object. self.ID='{self.ID}'")

    def __set_thumbnail_path(self):
        if self.SATELLITE_PRODUCT_TYPE == Sentinel1AProductType.RAW.value:
            logging.info(
                f"Sentinel-1A product type '{self.SATELLITE_PRODUCT_TYPE}' has no thumbnail image. self.ID={self.ID}")

        # Get thumbnail path
        if self.SATELLITE_PRODUCT_TYPE == Sentinel1AProductType.OCN.value:
            file_name = "quick-look-l2-owi.png"
        else:
            file_name = "quick-look.png"
        thumbnail_path_local = FileUtils.generate_path(
            self.DIRECTORY_PATH_LOCAL, "preview", file_name)

        # Set thumbnail path
        if os.path.exists(thumbnail_path_local):
            self.THUMBNAIL_IMG_PATH_LOCAL = thumbnail_path_local
            logging.debug(
                f"Set thumbnail image path local. self.ID='{self.ID}', self.THUMBNAIL_IMG_PATH_LOCAL='{self.THUMBNAIL_IMG_PATH_LOCAL}'")
        else:
            logging.error(
                f"Local thumbnail path does not exist. self.ID='{self.ID}', self.THUMBNAIL_IMG_PATH_LOCAL='{self.THUMBNAIL_IMG_PATH_LOCAL}'")

    def __set_time_info(self):
        # Get dict with time infos
        acquisitionPeriodDict = FileUtils.get_dict_value_by_key(
            self.MANIFEST_DICT, "safe:acquisitionPeriod")
        if acquisitionPeriodDict is None:
            logging.info(
                f"Could not get time info from 'manifest.safe'. self.SATELLITE_PRODUCT_TYPE='{self.SATELLITE_PRODUCT_TYPE}', self.ID='{self.ID}'")
            return

        # Set time infos
        self.PRODUCT_START_TIME = acquisitionPeriodDict["safe:startTime"]
        self.PRODUCT_STOP_TIME = acquisitionPeriodDict["safe:stopTime"]
        logging.debug(f"Set time infos. self.ID='{self.ID}'")

    def __upload_files(self):
        # Upload RGB img
        if self.RGB_IMG_PATH_LOCAL != "":
            rgb_destination_path = FileUtils.generate_path(
                "sid", self.SATELLITE_MISSION, self.ID, "images", "rgb")
            rgb_img_path_storage = FirebaseStorage.upload_file(
                rgb_destination_path, self.RGB_IMG_PATH_LOCAL)
            if rgb_img_path_storage != "":
                self.RGB_IMG_PATH_STORAGE = rgb_img_path_storage
            else:
                logging.error(
                    f"RGB image upload failed. self.ID='{self.ID}', self.RGB_IMG_PATH_LOCAL='{self.RGB_IMG_PATH_LOCAL}', rgb_destination_path='{rgb_destination_path}'")

        logging.debug(f"Uploaded files. self.ID='{self.ID}'")

    def __set_bands_paths(self):
        # Check if product type has TIFF files
        if self.SATELLITE_PRODUCT_TYPE in [Sentinel1AProductType.RAW.value, Sentinel1AProductType.OCN.value]:
            logging.info(
                f"Cannot set bands paths for Sentinel-1A product type: '{self.SATELLITE_PRODUCT_TYPE}' because not TIFF files available for this product type.")
            return

        # Get all tiff file names (local)
        measurement_path_local = FileUtils.generate_path(
            self.DIRECTORY_PATH_LOCAL, "measurement")
        file_names = os.listdir(measurement_path_local)
        file_paths_local = [FileUtils.generate_path(
            measurement_path_local, file_name) for file_name in file_names]

        # Get all tiff file names (storage)
        measurement_path_storage = FileUtils.generate_path(
            self.DIRECTORY_PATH_STORAGE, "measurement")
        file_paths_storage = [FileUtils.generate_path(
            measurement_path_storage, file_name) for file_name in file_names]

        # Bands local paths mapping
        for index, value in enumerate(file_names):
            band_idx = index + 1
            # Local
            self.BANDS_TIFF_PATHS_LOCAL[f"B0{band_idx}"] = next(
                (file_path for file_path in file_paths_local if f"b-00{band_idx}" in file_path), None)
            # Storage
            self.BANDS_TIFF_PATHS_STORAGE[f"B0{band_idx}"] = next(
                (file_path for file_path in file_paths_storage if f"b-00{band_idx}" in file_path), None)

        logging.debug(f"Set bands paths. self.ID='{self.ID}'")

    def __generate_rgb(self, save_path: str = FileUtils.generate_path(IMAGES_FILES_PATH, "sentinel-1a")):
        if self.SATELLITE_PRODUCT_TYPE != Sentinel1AProductType.SLC.value:
            logging.info(
                f"Cannot generate an RGB image. Needed Sentinel-1A producty type  '{Sentinel1AProductType.SLC}'. self.ID='{self.ID}', self.USER_ID={self.USER_ID}, self.SENTINEL1A_TYPE='{self.SATELLITE_PRODUCT_TYPE}'")
            return
        rgb_path_local = MetricsCalculator.create_rgb_img(
            sid_id=self.ID,
            blue_band_02=self.BANDS_TIFF_PATHS_LOCAL["B02"],
            green_band_03=self.BANDS_TIFF_PATHS_LOCAL["B03"],
            red_band_04=self.BANDS_TIFF_PATHS_LOCAL["B04"],
            save_location=save_path
        )

        if rgb_path_local != save_path:
            logging.error(
                f"Failed to generate RGB. self.ID='{self.ID}', save_path='{save_path}'")
            return
        else:
            self.RGB_IMG_PATH_LOCAL = rgb_path_local
            logging.debug(f"Generated RGB image. self.ID='{self.ID}'")

    def __set_coordinates(self):
        # Get coordinates from manifest file
        coordinates_string = FileUtils.get_dict_value_by_key(
            self.MANIFEST_DICT, "gml:coordinates")
        coordinates_pairs = coordinates_string.split()

        # Set coordinates
        west = float('inf')  # positive infinity
        east = float('-inf')  # negative infinity
        south = float('inf')  # positive infinity
        north = float('-inf')  # negative infinity
        for pair in coordinates_pairs:
            latitude, longitude = map(float, pair.split(','))
            self.WEST_BOUND_LONGITUDE = min(west, longitude)
            self.EAST_BOUND_LONGITUDE = max(east, longitude)
            self.SOUTH_BOUND_LATITUDE = min(south, latitude)
            self.NORTH_BOUND_LATITUDE = max(north, latitude)

        logging.debug(f"Set coordinates. self.ID='{self.ID}'")

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
                "satellite_mission": SatelliteMission.SENTINEL_2B.value,
            },

            "images": {
                "rgb": {
                    "img_path_storage": self.RGB_IMG_PATH_STORAGE,
                    "img_path_local": self.RGB_IMG_PATH_LOCAL,
                    "archived_img_paths": [],
                },
                "indexes": {
                    "ndvi": {
                    },
                    "moisture": {
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
                "directory_path_local": self.DIRECTORY_PATH_LOCAL,
                "directory_path_storage": self.DIRECTORY_PATH_STORAGE,
                "manifest_path_local": self.MANIFEST_PATH_LOCAL,
                "manifest_path_storage": self.MANIFEST_PATH_STORAGE,
            },

            "capture_information": {
                "product_start_time": self.PRODUCT_START_TIME,
                "product_stop_time": self.PRODUCT_STOP_TIME,
                "product_type": self.SATELLITE_PRODUCT_TYPE,
            },
        }
