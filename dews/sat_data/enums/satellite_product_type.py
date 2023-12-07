from enum import Enum


class Sentinel1AProductType(Enum):
    UNKNOWN = "unknown"
    GRD = "grd"
    GRD_COG = "grd cog"
    OCN = "ocn"
    RAW = "raw"
    SLC = "slc"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in Sentinel1AProductType]


class Sentinel2BProductType(Enum):
    MSI = "msi"
    L2A = "l2a"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in Sentinel2BProductType]
