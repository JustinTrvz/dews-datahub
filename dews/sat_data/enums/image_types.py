from enum import Enum


class ImageType(Enum):
    '''Image types for every index (e.g. NDVI) used and additionally the RGB image.'''
    UNKNOWN = "unknown"
    RGB = "rgb"
    NDVI = "ndvi"
    EVI = "evi"
    MOISTURE = "moisture"
    NDWI = "ndwi"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in ImageType]