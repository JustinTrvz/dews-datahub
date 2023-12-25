from enum import Enum


class SatBand(Enum):
    """ Satellite bands like band AOT, 01, 02, 8A, etc. """
    AOT = "aot"
    SCL = "scl"
    TCI = "tci"
    WVP = "wvp"
    B01 = "b01"
    B02 = "b02"
    B03 = "b03"
    B04 = "b04"
    B05 = "b05"
    B06 = "b06"
    B07 = "b07"
    B08 = "b08"
    B8A = "b8a"
    B09 = "b09"
    B10 = "b10"
    B11 = "b11"
    B12 = "b12"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in SatBand]