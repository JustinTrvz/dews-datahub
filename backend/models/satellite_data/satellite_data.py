import datetime
import uuid
from models.init_vars import InitVar

from models.satellite_data.satellite_mission import SatelliteMission



class SatelliteData():
    """Satellite data root class. Every satellite types should inherit from this class."""

    # Basic info
    ID = InitVar.EMPTY.value  # identifier
    USER_ID = InitVar.EMPTY.value  # owner of the satellite data
    AREA_NAME = InitVar.UNKNOWN.value  # can be a custom/fictional area name
    SATELLITE_MISSION = InitVar.UNKNOWN.value
    SATELLITE_PRODUCT_TYPE = InitVar.UNKNOWN.value
    PRODUCT_START_TIME = datetime.datetime.now()
    PRODUCT_STOP_TIME = datetime.datetime.now()

    # Area info
    CITY = InitVar.UNKNOWN.value  # city where satellite data was taken
    COUNTRY = InitVar.UNKNOWN.value  # country where satellite data was taken
    POSTAL_CODE = InitVar.MINUS_INT.value  # postal code where satellite data was taken

    # Time info
    CREATION_TIME = datetime.datetime.now()  # time stamp when this object was created
    CAPTURE_TIME = datetime.datetime.now()  # time stamp when satellite data was captured

    # Coordinates info
    WEST_BOUND_LONGITUDE = InitVar.MINUS_INT.value
    EAST_BOUND_LONGITUDE = InitVar.MINUS_INT.value
    SOUTH_BOUND_LATITUDE = InitVar.MINUS_INT.value
    NORTH_BOUND_LATITUDE = InitVar.MINUS_INT.value

    # File paths
    ## Thumbnail
    THUMBNAIL_IMG_PATH_LOCAL = InitVar.EMPTY.value  # path to local image
    THUMBNAIL_IMG_PATH_STORAGE = InitVar.EMPTY.value  # path to remote image in file storage
    ## Directory
    DIRECTORY_PATH_LOCAL = InitVar.EMPTY.value  # path to local extracted directory
    DIRECTORY_PATH_STORAGE = InitVar.EMPTY.value  # path to remote extracted directory in file storage

    def __init__(self, directory_path_local: str, user_id: str, area_name: str = InitVar.UNKNOWN.value, satellite_mission: str = InitVar.UNKNOWN.value,
                 city: str = InitVar.UNKNOWN.value, country: str = InitVar.UNKNOWN.value, postal_code: int = InitVar.MINUS_INT.value) -> None:
        # Validate input data before init
        if not (satellite_mission in [mission.value for mission in SatelliteMission]):
            print(satellite_mission)
            print(dir(SatelliteMission))
            raise Exception(f"Satellite mission '{satellite_mission}' is not accepted!")
        # Init variables
        self.DIRECTORY_PATH_LOCAL = directory_path_local
        self.ID = uuid.uuid4()
        self.USER_ID = user_id
        self.AREA_NAME = area_name
        self.SATELLITE_MISSION = satellite_mission
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

    @staticmethod
    def from_json(json_data) -> None:
        directory_path_local=json_data["directory_path_local"],
        user_id=json_data["user_id"],
        area_name=json_data["area_name"],
        satellite_mission=json_data["satellite_mission"],
        city=json_data["city"],
        country=json_data["country"],
        postal_code=json_data["postal_code"],

        if satellite_mission == SatelliteMission.SENTINEL_1A.value:
            # Sentinel-1A
            from models.satellite_data.sentinel_1.sentinel1a_data import Sentinel1AData
            return Sentinel1AData(
                directory_path_local=directory_path_local,
                user_id=user_id,
                area_name=area_name,
                satellite_mission=satellite_mission,
                city=city,
                country=country,
                postal_code=postal_code
            )
        elif satellite_mission == SatelliteMission.SENTINEL_2B.value:
            # Sentinel-2B
            from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData
            return Sentinel2BData(
                directory_path_local=directory_path_local,
                user_id=user_id,
                area_name=area_name,
                satellite_mission=satellite_mission,
                city=city,
                country=country,
                postal_code=postal_code
            )
        else:
            # Unknown
            return SatelliteData(
                directory_path_local=directory_path_local,
                user_id=user_id,
                area_name=area_name,
                satellite_mission=satellite_mission,
                city=city,
                country=country,
                postal_code=postal_code
            )