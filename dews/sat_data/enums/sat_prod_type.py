from enum import Enum


class SatProdType(Enum):
    UNKNOWN = "unknown"

    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in SatProdType]


class Sentinel1AProdType(Enum):
    UNKNOWN = "unknown"
    GRD = "grd"
    GRD_COG = "grd cog"
    OCN = "ocn"
    RAW = "raw"
    SLC = "slc"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in Sentinel1AProdType]


class Sentinel2BProductType(Enum):
    MSI = "msi"
    L2A = "l2a"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in Sentinel2BProductType]
