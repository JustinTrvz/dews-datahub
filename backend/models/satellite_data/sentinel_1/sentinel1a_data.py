import logging

from backend.data.models.init_vars import InitVar
from backend.data.models.satellite_data.sentinel_1.sentinel1a_product_types import Sentinel1AProductType
from backend.data.models.satellite_data.satellite_data import SatelliteData


class Sentinel1AData(SatelliteData):
    """ Sentinel1AData inherits from SatelliteData"""
    # Files and directories paths
    MEASURMENT_PATH_STORAGE = InitVar.UNKNOWN  # contains .tiff files
    MEASURMENT_PATH_LOCAL = InitVar.UNKNOWN
    MANIFEST_PATH_STORAGE = InitVar.UNKNOWN  # contains meta data
    MANIFEST_PATH_LOCAL = InitVar.UNKNOWN
    SENTINEL1A_TYPE = InitVar.UNKNOWN

    # Image paths
    ## Band 1 TIFF
    BAND_1_TIFF_PATH_LOCAL = InitVar.EMPTY
    BAND_1_TIFF_PATH_STORAGE = InitVar.EMPTY
    ## Band 2 TIFF
    BAND_2_TIFF_PATH_LOCAL = InitVar.EMPTY
    BAND_2_TIFF_PATH_STORAGE = InitVar.EMPTY
    ## Band 3 TIFF
    BAND_3_TIFF_PATH_LOCAL = InitVar.EMPTY
    BAND_3_TIFF_PATH_STORAGE = InitVar.EMPTY
    ## Band 4 TIFF
    BAND_4_TIFF_PATH_LOCAL = InitVar.EMPTY
    BAND_4_TIFF_PATH_STORAGE = InitVar.EMPTY
    ## Band 5 TIFF
    BAND_5_TIFF_PATH_LOCAL = InitVar.EMPTY
    BAND_5_TIFF_PATH_STORAGE = InitVar.EMPTY
    ## Band 6 TIFF
    BAND_6_TIFF_PATH_LOCAL = InitVar.EMPTY
    BAND_6_TIFF_PATH_STORAGE = InitVar.EMPTY
    ## All TIFF img paths
    BANDS_TIFF_PATHS_LOCAL = {
        "B01": BAND_1_TIFF_PATH_LOCAL,
        "B02": BAND_2_TIFF_PATH_LOCAL,
        "B03": BAND_3_TIFF_PATH_LOCAL,
        "B04": BAND_4_TIFF_PATH_LOCAL,
        "B05": BAND_5_TIFF_PATH_LOCAL,
        "B06": BAND_6_TIFF_PATH_LOCAL,
    }
    BANDS_TIFF_PATHS_STORAGE = {
        "B01": BAND_1_TIFF_PATH_STORAGE,
        "B02": BAND_2_TIFF_PATH_STORAGE,
        "B03": BAND_3_TIFF_PATH_STORAGE,
        "B04": BAND_4_TIFF_PATH_STORAGE,
        "B05": BAND_5_TIFF_PATH_STORAGE,
        "B06": BAND_6_TIFF_PATH_STORAGE,
    }
    ## Band 1 PNG
    BAND_1_PNG_PATH_LOCAL = InitVar.EMPTY
    BAND_1_PNG_PATH_STORAGE = InitVar.EMPTY
    ## Band 2 PNG
    BAND_2_PNG_PATH_LOCAL = InitVar.EMPTY
    BAND_2_PNG_PATH_STORAGE = InitVar.EMPTY
    ## Band 3 PNG
    BAND_3_PNG_PATH_LOCAL = InitVar.EMPTY
    BAND_3_PNG_PATH_STORAGE = InitVar.EMPTY
    ## Band 4 PNG
    BAND_4_PNG_PATH_LOCAL = InitVar.EMPTY
    BAND_4_PNG_PATH_STORAGE = InitVar.EMPTY
    ## Band 5 PNG
    BAND_5_PNG_PATH_LOCAL = InitVar.EMPTY
    BAND_5_PNG_PATH_STORAGE = InitVar.EMPTY
    ## Band 6 PNG
    BAND_6_PNG_PATH_LOCAL = InitVar.EMPTY
    BAND_6_PNG_PATH_STORAGE = InitVar.EMPTY
    ## All PNG img paths
    BANDS_PNG_PATHS_LOCAL = {
        "B01": BAND_1_PNG_PATH_LOCAL,
        "B02": BAND_2_PNG_PATH_LOCAL,
        "B03": BAND_3_PNG_PATH_LOCAL,
        "B04": BAND_4_PNG_PATH_LOCAL,
        "B05": BAND_5_PNG_PATH_LOCAL,
        "B06": BAND_6_PNG_PATH_LOCAL,
    }
    BANDS_PNG_PATHS_STORAGE = {
        "B01": BAND_1_PNG_PATH_STORAGE,
        "B02": BAND_2_PNG_PATH_STORAGE,
        "B03": BAND_3_PNG_PATH_STORAGE,
        "B04": BAND_4_PNG_PATH_STORAGE,
        "B05": BAND_5_PNG_PATH_STORAGE,
        "B06": BAND_6_PNG_PATH_STORAGE,
    }

    def __init__(self, user_id: str, area_name: str = InitVar.UNKNOWN, satellite_type: str = InitVar.UNKNOWN,
                 city: str = InitVar.UNKNOWN, country: str = InitVar.UNKNOWN, postal_code: int = InitVar.POSTAL_CODE_FILLER,
                 sentinel1a_type: str = Sentinel1AProductType.UNKNOWN) -> None:
        super().__init__(user_id, area_name, satellite_type, city, country, postal_code)
        self.SENTINEL1A_TYPE = sentinel1a_type

    def generate_rgb(self):
        if self.SENTINEL1A_TYPE != Sentinel1AProductType.SLC:
            logging.warning(f"Cannot generate an RGB image. Needed Sentinel-1A type: '{Sentinel1AProductType.SLC}' but is '{self.SENTINEL1A_TYPE}'. self.ID='{self.ID}', self.USER_ID={self.USER_ID}, self.SENTINEL1A_TYPE='{self.SENTINEL1A_TYPE}'")

    def tiff_to_png(self):
        if self.SENTINEL1A_TYPE == Sentinel1AProductType.RAW:
            logging.warning(f"Cannot convert TIFF to PNG because the Sentinel-1A data's type is '{Sentinel1AProductType.RAW}'. self.ID='{self.ID}'")
            return ""
