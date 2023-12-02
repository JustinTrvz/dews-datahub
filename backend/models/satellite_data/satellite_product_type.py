from enum import Enum


class Sentinel1AProductType(Enum):
    UNKNOWN = "unknown"
    GRD = "grd"
    GRD_COG = "grd cog"
    OCN = "ocn"
    RAW = "raw"
    SLC = "slc"


class Sentinel2BProductType(Enum):
    MSI = "msi"
    L2A = "l2a"
