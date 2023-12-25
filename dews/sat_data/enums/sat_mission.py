from enum import Enum
import os
import logging

logger = logging.getLogger("django")

class SatMission(Enum):
    UNKNOWN = "unknown"
    SENTINEL_1A = "sentinel-1a"
    SENTINEL_1B = "sentinel-1b"
    SENTINEL_2A = "sentinel-2a"
    SENTINEL_2B = "sentinel-2b"
    SENTINEL_3A = "sentinel-3a"
    SENTINEL_3B = "sentinel-3b"
    SENTINEL_5P = "sentinel-5p"
    LANDSAT_1 = "landsat-1"
    LANDSAT_2 = "landsat-2"
    LANDSAT_3 = "landsat-3"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in SatMission]
    
    @staticmethod
    def get_mission_by_filename(filename: str):
        filename = str(filename)
        logger.debug(f"File name: {filename}")
        file_basename = os.path.basename(filename)
        logger.debug(f"File basename: {file_basename}")
        if "S1A" in file_basename:
            return SatMission.SENTINEL_1A.value
        if "S1B" in file_basename:
            return SatMission.SENTINEL_1B.value
        elif "S2A" in file_basename:
            return SatMission.SENTINEL_2A.value
        elif "S2B" in file_basename:
            return SatMission.SENTINEL_2B.value
        elif "S3A" in file_basename:
            return SatMission.SENTINEL_3A.value
        elif "S3B" in file_basename:
            return SatMission.SENTINEL_3B.value
        elif "S5P" in file_basename:
            return SatMission.SENTINEL_5P.value
        else:
            return SatMission.UNKNOWN.value