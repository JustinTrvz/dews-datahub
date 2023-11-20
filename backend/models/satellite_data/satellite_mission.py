from enum import Enum


class SatelliteMission(Enum):
    UNKNOWN = "Unknown"
    SENTINEL_1A = "Sentinel-1A"
    SENTINEL_1B = "Sentinel-1B"
    SENTINEL_2A = "Sentinel-2A"
    SENTINEL_2B = "Sentinel-2B"
    LANDSAT_1 = "Landsat-1"
    LANDSAT_2 = "Landsat-2"
    LANDSAT_3 = "Landsat-3"
