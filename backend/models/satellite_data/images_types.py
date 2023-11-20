from enum import Enum


class ImageType(Enum):
    '''Image types for every index (e.g. NDVI) used and additionally the RGB image.'''
    UNKNOWN = "Unknown"
    RGB = "rgb"
    NDVI = "ndvi"
    MOISTURE = "moisture"
    NDWI = "ndwi"
