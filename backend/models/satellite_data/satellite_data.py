import datetime
import uuid

from backend.data.models.satellite_data.satellite_types import SatelliteType


class SatelliteData():
    """Satellite data root class. Every satellite types should inherit from this class."""

    # Basic info
    ID = ""  # identifier
    USER_ID = ""  # owner of the satellite data
    AREA_NAME = ""  # can be a custom/fictional area name
    SATELLITE_TYPE = ""

    # Area info
    CITY = ""  # city where satellite data was taken
    COUNTRY = ""  # country where satellite data was taken
    POSTAL_CODE = ""  # postal code where satellite data was taken

    # Time info
    CREATION_TIME = datetime.now()  # time stamp when this object was created
    CAPTURE_TIME = datetime.now()  # time stamp when satellite data was captured

    # Coordinates info
    WEST_BOUND_LONGITUDE = ""
    EAST_BOUND_LONGITUDE = ""
    SOUTH_BOUND_LATITUDE = ""
    NORTH_BOUND_LATITUDE = ""

    # Storage paths
    THUMBNAIL_IMG_PATH_LOCAL = ""  # path to local image
    THUMBNAIL_IMG_PATH_STORAGE = ""  # path to remote image in file storage
    DIRECTORY_PATH_LOCAL = ""  # path to local extracted directory
    DIRECTORY_PATH_STORAGE = ""  # path to remote extracted directory in file storage

    def __init__(self, user_id: str, area_name: str = "Unknown", satellite_type: str = "Unknown", city: str = "Unknown", country: str = "Unknown", postal_code: int = 0) -> None:
        # Validate input data before init
        if not (satellite_type in dir(SatelliteType)):
            raise Exception(f"Satellite type '{satellite_type}' is not accepted!")
        # Init variables
        self.ID = uuid.uuid4()
        self.USER_ID = user_id
        self.AREA_NAME = area_name
        self.SATELLITE_TYPE = satellite_type
        self.CITY = city
        self.COUNTRY = country
        self.POSTAL_CODE = postal_code

    # Basic info
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

    # Storage paths
    def set_thumbnail_img_path_local(self, thumbnail_img_path_local: str) -> None:
        self.THUMBNAIL_IMG_PATH_LOCAL = thumbnail_img_path_local

    def set_thumbnail_img_path_storage(self, thumbnail_img_path_storage: str) -> None:
        self.THUMBNAIL_IMG_PATH_STORAGE = thumbnail_img_path_storage

    def set_directory_path_local(self, directory_path_local: str) -> None:
        self.DIRECTORY_PATH_LOCAL = directory_path_local

    def set_directory_path_storage(self, directory_path_storage: str) -> None:
        self.DIRECTORY_PATH_STORAGE = directory_path_storage
