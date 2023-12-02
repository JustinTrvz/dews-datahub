import datetime
import logging
import uuid

from backend.models.satellite_data.satellite_product_type import Sentinel1AProductType
from backend.models.init_vars import InitVar
from backend.models.satellite_data.satellite_mission import SatelliteMission


class SatelliteData():
    """Satellite data root class. Every satellite types should inherit from this class."""

    # Basic info
    ID = str(uuid.uuid4())  # identifier
    USER_ID = InitVar.EMPTY.value  # owner of the satellite data
    AREA_NAME = InitVar.UNKNOWN.value  # can be a custom/fictional area name
    MISSION = InitVar.UNKNOWN.value
    PRODUCT_TYPE = InitVar.UNKNOWN.value
    PRODUCT_START_TIME = datetime.datetime.now()
    PRODUCT_STOP_TIME = datetime.datetime.now()

    # Area info
    CITY = InitVar.UNKNOWN.value  # city where satellite data was taken
    COUNTRY = InitVar.UNKNOWN.value  # country where satellite data was taken
    # postal code where satellite data was taken
    POSTAL_CODE = InitVar.MINUS_INT.value

    # Time info
    # time stamp when this object was created
    CREATION_TIME = datetime.datetime.now()
    # time stamp when satellite data was captured
    CAPTURE_TIME = datetime.datetime.now()

    # Coordinates info
    WEST_BOUND_LONGITUDE = InitVar.MINUS_INT.value
    EAST_BOUND_LONGITUDE = InitVar.MINUS_INT.value
    SOUTH_BOUND_LATITUDE = InitVar.MINUS_INT.value
    NORTH_BOUND_LATITUDE = InitVar.MINUS_INT.value

    # File paths
    # Thumbnail
    THUMBNAIL_PATH = InitVar.EMPTY.value  # path to local image
    # Directory
    DIRECTORY_PATH = InitVar.EMPTY.value  # path to local extracted directory

    def __init__(self, directory_path: str, user_id: str, area_name: str = InitVar.UNKNOWN.value, mission: str = InitVar.UNKNOWN.value,
                 city: str = InitVar.UNKNOWN.value, country: str = InitVar.UNKNOWN.value, postal_code: int = InitVar.MINUS_INT.value) -> None:
        logging.debug(f"Initalizing SatelliteData object. self.ID='{self.ID}'")
        # Validate input data before init
        if not (mission in [m.value for m in SatelliteMission]):
            print(mission)
            print(dir(SatelliteMission))
            raise Exception(
                f"Satellite mission '{mission}' is not accepted!")
        # Init variables
        self.DIRECTORY_PATH = directory_path
        self.USER_ID = user_id
        self.AREA_NAME = area_name
        self.MISSION = mission.lower()
        # self.PRODUCT_TYPE must be set in child class!
        self.CITY = city
        self.COUNTRY = country
        self.POSTAL_CODE = postal_code

    # Basic info
    def set_product_type(self, product_type) -> None:
        self.PRODUCT_TYPE = product_type

    def set_area_name(self, area_name: str) -> None:
        self.AREA_NAME = area_name

    # Area info
    def set_city(self, city: str) -> None:
        self.CITY = city

    def set_country(self, country: str) -> None:
        self.COUNTRY = country

    def set_postal_code(self, postal_code: str) -> None:
        self.POSTAL_CODE = postal_code

    # Time info
    def set_capture_time(self, capture_time: datetime) -> None:
        self.CAPTURE_TIME = capture_time

    # Paths
    def set_thumbnail_img_path(self, thumbnail_img_path: str) -> None:
        self.THUMBNAIL_PATH = thumbnail_img_path

    def set_directory_path(self, directory_path: str) -> None:
        self.DIRECTORY_PATH = directory_path

    @staticmethod
    def create(directory_path: str, user_id: str, area_name: str = InitVar.UNKNOWN.value,
               mission: str = InitVar.UNKNOWN.value, city: str = InitVar.UNKNOWN.value,
               country: str = InitVar.UNKNOWN.value, postal_code: int = InitVar.MINUS_INT.value):
        if mission == SatelliteMission.SENTINEL_1A.value:
            # Sentinel-1A
            logging.debug(
                f"Identified '{mission}' dataset. directory_path='{directory_path}', user_id='{user_id}', area_name='{area_name}'")
            from models.satellite_data.sentinel_1.sentinel1a_data import Sentinel1AData
            return Sentinel1AData(
                directory_path=directory_path,
                user_id=user_id,
                area_name=area_name,
                city=city,
                country=country,
                postal_code=postal_code,
            )
        elif mission == SatelliteMission.SENTINEL_2B.value:
            # Sentinel-2B
            logging.debug(
                f"Identified '{mission}' dataset. directory_path_local='{directory_path}', user_id='{user_id}', area_name='{area_name}'")
            from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData
            return Sentinel2BData(
                directory_path=directory_path,
                user_id=user_id,
                area_name=area_name,
                city=city,
                country=country,
                postal_code=postal_code,
            )

    @staticmethod
    def from_json(json_data: dict):
        print("JSON: ", json_data)

        directory_path = json_data["directory_path"]
        user_id = json_data["user_id"]
        area_name = json_data["area_name"]
        mission = json_data["mission"].lower()
        city = json_data["city"]
        country = json_data["country"]
        postal_code = json_data["postal_code"]

        if mission == SatelliteMission.SENTINEL_1A.value:
            # Sentinel-1A
            logging.debug(
                f"Identified {mission} dataset. directory_path='{directory_path}', user_id='{user_id}', area_name='{area_name}'")
            from models.satellite_data.sentinel_1.sentinel1a_data import Sentinel1AData
            return Sentinel1AData(
                directory_path=directory_path,
                user_id=user_id,
                area_name=area_name,
                city=city,
                country=country,
                postal_code=postal_code,
                product_type=Sentinel1AProductType.GRD.value  # TODO: get product type
            )
        elif mission == SatelliteMission.SENTINEL_2B.value:
            # Sentinel-2B
            logging.debug(
                f"Identified {mission} dataset. directory_path_local='{directory_path}', user_id='{user_id}', area_name='{area_name}'")
            from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData
            return Sentinel2BData(
                directory_path=directory_path,
                user_id=user_id,
                area_name=area_name,
                satellite_mission=mission,
                city=city,
                country=country,
                postal_code=postal_code
            )
        else:
            # Unknown
            return SatelliteData(
                directory_path=directory_path,
                user_id=user_id,
                area_name=area_name,
                mission=mission,
                city=city,
                country=country,
                postal_code=postal_code
            )
