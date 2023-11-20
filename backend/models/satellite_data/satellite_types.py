from enum import Enum


class SatelliteType(Enum):
    UNKNOWN = "Unknown"
    SENTINEL_2A = "Sentinel-2A"
    SENTINEL_2B = "Sentinel-2B"
    LANDSAT_1 = "Landsat-1"
    LANDSAT_2 = "Landsat-2"
    LANDSAT_3 = "Landsat-3"
