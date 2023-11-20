from enum import Enum


class Sentinel1AProductType(Enum):
    UNKNOWN = "Unknown"
    GRD = "GRD"
    GRD_COG = "GRD COG"
    OCN = "OCN"
    RAW = "RAW"
    SLC = "SLC"
