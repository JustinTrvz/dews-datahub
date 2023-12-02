import logging
from backend.models.satellite_data.satellite_mission import SatelliteMission
from backend.models.satellite_data.statistics.metrics_calculator import MetricsCalculator
from backend.models.satellite_data.utils.file_utils import FileUtils

from backend.models.init_vars import InitVar
from backend.models.satellite_data.satellite_product_type import Sentinel1AProductType
from backend.models.satellite_data.satellite_data import SatelliteData
from backend.models.satellite_data.images_types import ImageType

from config import *
from backend.database.psql_client import PSQLClient as DbClient
from backend.database.models import BoundLatitudes, CaptureInfo, DbSatelliteData, AreaInfo, ImageInfo


class Sentinel1AData(SatelliteData):
    """ Sentinel1AData inherits from SatelliteData"""
    # Files and directories paths
    # Measurment directory
    MEASURMENT_PATH = InitVar.UNKNOWN.value  # directory which contains .tiff files
    # Manifest file
    MANIFEST_PATH = InitVar.UNKNOWN.value  # XML file which contains meta data
    MANIFEST_DICT = {}

    # TIFF Image paths
    BANDS_TIFF_PATHS = {
        "B01": InitVar.EMPTY.value,
        "B02": InitVar.EMPTY.value,
        "B03": InitVar.EMPTY.value,
        "B04": InitVar.EMPTY.value,
        "B05": InitVar.EMPTY.value,
        "B06": InitVar.EMPTY.value,
    }

    # Generated images paths
    RGB_IMG_PATH = InitVar.EMPTY.value
    NDVI_IMG_PATH = InitVar.EMPTY.value
    MOISTURE_IMG_PATH = InitVar.EMPTY.value

    def __init__(self, directory_path: str,
                 user_id: str,
                 area_name: str = InitVar.UNKNOWN.value,
                 city: str = InitVar.UNKNOWN.value,
                 country: str = InitVar.UNKNOWN.value,
                 postal_code: int = InitVar.MINUS_INT.value,
                 product_type: str = Sentinel1AProductType.UNKNOWN.value) -> None:
        # Init from parent class
        logging.debug(
            f"Initalizing Sentinel1AData object. self.ID='{self.ID}'")
        super().__init__(directory_path,
                         user_id,
                         area_name,
                         SatelliteMission.SENTINEL_1A.value,
                         city,
                         country,
                         postal_code)
        # Mission specific attributes
        self.set_product_type(product_type)
        # Manifest info
        self.set_manifest_info()
        # Functions that set attributes
        self.set_thumbnail_path()
        self.set_coordinates()
        self.set_time_info()
        self.set_bands_paths()
        # Generations, calculations, uploads, etc.
        self.generate_rgb()
        if self.save() == "":
            return logging.error(f"Failed creating Sentinel1AData object. self.ID='{self.ID}'")

        # Debug log
        return logging.debug(
            f"Finished creating Sentinel1AData object. self.ID='{self.ID}'")

    def set_manifest_info(self):
        self.MANIFEST_PATH = FileUtils.generate_path(
            self.DIRECTORY_PATH, S1A_MANIFEST_FILE_NAME)
        self.MANIFEST_DICT = FileUtils.xml_to_dict(self.MANIFEST_PATH)

    def set_thumbnail_path(self):
        if self.PRODUCT_TYPE == Sentinel1AProductType.RAW.value:
            logging.info(
                f"Sentinel-1A product type '{self.PRODUCT_TYPE}' has no thumbnail image. self.ID={self.ID}")
            return

        # Get thumbnail path
        if self.PRODUCT_TYPE == Sentinel1AProductType.OCN.value:
            file_name = "quick-look-l2-owi.png"
        else:
            file_name = "quick-look.png"
        thumbnail_path = FileUtils.generate_path(
            self.DIRECTORY_PATH, "preview", file_name)

        # Set thumbnail path
        if os.path.exists(thumbnail_path):
            self.THUMBNAIL_PATH = thumbnail_path
            logging.debug(
                f"Set thumbnail image path local. self.ID='{self.ID}', self.THUMBNAIL_IMG_PATH_LOCAL='{self.THUMBNAIL_PATH}'")
        else:
            logging.error(
                f"Local thumbnail path does not exist. self.ID='{self.ID}', self.THUMBNAIL_IMG_PATH_LOCAL='{self.THUMBNAIL_PATH}'")

    def set_time_info(self):
        # Get dict with time infos
        acquisitionPeriodDict = FileUtils.get_dict_value_by_key(
            self.MANIFEST_DICT, "safe:acquisitionPeriod")
        if acquisitionPeriodDict is None:
            logging.info(
                f"Could not get time info from 'manifest.safe'. self.PRODUCT_TYPE='{self.PRODUCT_TYPE}', self.ID='{self.ID}'")
            return

        # Set time infos
        self.PRODUCT_START_TIME = acquisitionPeriodDict["safe:startTime"]
        self.PRODUCT_STOP_TIME = acquisitionPeriodDict["safe:stopTime"]
        logging.debug(f"Set time infos. self.ID='{self.ID}'")

    def save(self) -> str:
        """
        Saves satellite data info to database.

        Returns empty string on failure and id on success.
        """
        # Create entry in database
        id, object = DbClient.create(
            DbSatelliteData,
            # Basic info
            id=self.ID,
            mission=self.MISSION,
            product_type=self.PRODUCT_TYPE,
            # Path info
            directory_path=self.DIRECTORY_PATH,
            manifest_path=self.MANIFEST_PATH,
            # Foreign keys
            user_id=DB_USER,
            # Area info
            area_info=AreaInfo(
                area_name=self.AREA_NAME,
                country=self.COUNTRY,
                city=self.CITY,
                postal_code=self.POSTAL_CODE,
                creation_time=self.CREATION_TIME,
                capture_time=self.CAPTURE_TIME,
            ),
            # Bound latitudes
            bound_latitudes=BoundLatitudes(
                north=self.NORTH_BOUND_LATITUDE,
                east=self.EAST_BOUND_LONGITUDE,
                south=self.SOUTH_BOUND_LATITUDE,
                west=self.WEST_BOUND_LONGITUDE,
            ),
            # Capture info
            capture_info=CaptureInfo(
                product_start_time=self.PRODUCT_START_TIME,
                product_stop_time=self.PRODUCT_STOP_TIME,
                product_type=self.PRODUCT_TYPE,
            ),
            # Image info
            image_info=[
                ImageInfo(
                    img_type=ImageType.RGB.value,
                    img_path=self.RGB_IMG_PATH,
                    archived_img_paths="",
                ),
                ImageInfo(
                    img_type=ImageType.NDVI.value,
                    img_path=self.NDVI_IMG_PATH,
                    archived_img_paths="",
                ),
                ImageInfo(
                    img_type=ImageType.MOISTURE.value,
                    img_path=self.MOISTURE_IMG_PATH,
                    archived_img_paths="",
                ),
            ],
        )

        if id is None or object is None:
            logging.error(
                f"Failed to add Sentinel1AData object to database. id='{id}', object='{object}', self.ID='{self.ID}'")
            return ""

        logging.debug(f"Adding to database complete. id='{self.ID}'")
        return id

    def set_bands_paths(self):
        # Check if product type has TIFF files
        if self.PRODUCT_TYPE in [Sentinel1AProductType.RAW.value, Sentinel1AProductType.OCN.value]:
            logging.info(
                f"Cannot set bands paths for Sentinel-1A product type: '{self.PRODUCT_TYPE}' because not TIFF files available for this product type.")
            return

        # Get all tiff file names
        measurement_path = FileUtils.generate_path(
            self.DIRECTORY_PATH, "measurement")
        file_names = os.listdir(measurement_path)
        file_paths_local = [FileUtils.generate_path(
            measurement_path, file_name) for file_name in file_names]

        # Bands paths mapping
        for index, _ in enumerate(file_names):
            band_idx = index + 1
            self.BANDS_TIFF_PATHS[f"B0{band_idx}"] = next(
                (file_path for file_path in file_paths_local if f"b-00{band_idx}" in file_path), None)

        logging.debug(f"Set bands paths. self.ID='{self.ID}'")

    def generate_rgb(self, save_path: str = FileUtils.generate_path(IMAGES_FILES_PATH, SatelliteMission.SENTINEL_1A.value)):
        if self.PRODUCT_TYPE != Sentinel1AProductType.SLC.value:
            logging.info(
                f"Cannot generate an RGB image. Needed '{self.MISSION}' product type is '{Sentinel1AProductType.SLC}'. self.ID='{self.ID}', self.USER_ID='{self.USER_ID}', self.SENTINEL1A_TYPE='{self.PRODUCT_TYPE}'")
            return
        rgb_path = MetricsCalculator.create_rgb_img(
            sid_id=self.ID,
            blue_band_02=self.BANDS_TIFF_PATHS["B02"],
            green_band_03=self.BANDS_TIFF_PATHS["B03"],
            red_band_04=self.BANDS_TIFF_PATHS["B04"],
            save_location=save_path
        )

        if rgb_path != save_path:
            logging.error(
                f"Failed to generate RGB. self.ID='{self.ID}', save_path='{save_path}'")
            return
        else:
            self.RGB_IMG_PATH = rgb_path
            logging.debug(f"Generated RGB image. self.ID='{self.ID}'")

    def set_coordinates(self):
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
                "satellite_mission": SatelliteMission.SENTINEL_2B.value,
                "area_name": self.AREA_NAME,
                "country": self.COUNTRY,
                "city": self.CITY,
                "postal_code": self.POSTAL_CODE,
                "creation_time": self.CREATION_TIME.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                "capture_time": self.CAPTURE_TIME.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            },

            "images": {
                "rgb": {
                    "img_path": self.RGB_IMG_PATH,
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
                "directory_path": self.DIRECTORY_PATH,
                "manifest_path": self.MANIFEST_PATH,
            },

            "capture_information": {
                "product_start_time": self.PRODUCT_START_TIME,
                "product_stop_time": self.PRODUCT_STOP_TIME,
                "product_type": self.PRODUCT_TYPE,
            },
        }
