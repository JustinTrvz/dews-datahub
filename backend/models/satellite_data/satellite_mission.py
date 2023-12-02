from enum import Enum


class SatelliteMission(Enum):
    UNKNOWN = "unknown"
    SENTINEL_1A = "sentinel-1a"
    SENTINEL_1B = "sentinel-1b"
    SENTINEL_2A = "sentinel-2a"
    SENTINEL_2B = "sentinel-2b"
    LANDSAT_1 = "landsat-1"
    LANDSAT_2 = "landsat-2"
    LANDSAT_3 = "landsat-3"
