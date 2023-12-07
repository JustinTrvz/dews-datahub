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

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in SatelliteMission]

    @staticmethod
    def as_tuple():
        """ Used for `choices` in `models.py`."""
        return {
            "sentinel": {"sentinel-1a": "Sentinel-1A", "sentinel-1b": "Sentinel-1B", "sentinel-2a": "Sentinel-2A", "sentinel-2b": "Sentinel-2B"},
            "landsat": {"landsat-1": "Landsat-1", "landsat-2": "Landsat-2", "landsat-3": "Landsat-3"},
            "unknown": "unknown"
        }
