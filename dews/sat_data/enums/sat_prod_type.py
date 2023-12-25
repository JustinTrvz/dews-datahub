from enum import Enum


class SatProdType(Enum):
    UNKNOWN = "unknown"

    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in SatProdType]


class S1AProdType(Enum):
    UNKNOWN = "unknown"
    GRD = "grd"
    GRD_COG = "grd cog"
    OCN = "ocn"
    RAW = "raw"
    SLC = "slc"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in S1AProdType]


class S1BProdType(Enum):
    UNKNOWN = "unknown"

    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in S1BProdType]

class S2AProdType(Enum):
    UNKNOWN = "unknown"
    S2MSI1C = "s2msi1c"
    S2MSI2A = "s2msi2a"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in S2AProdType]

class S2BProdType(Enum):
    UNKNOWN = "unknown"
    S2MSI1C = "s2msi1c"
    S2MSI2A = "s2msi2a"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in S2BProdType]


class S3AProdType(Enum):
    UNKNOWN = "unknown"
    # OLCI
    OL_1_EFR = "ol_1_efr___"
    OL_1_ERR = "ol_1_err___"
    OL_2_LFR = "ol_2_lfr___"
    OL_2_LRR = "ol_2_lrr___"
    OL_2_WFR = "ol_2_wfr___"
    OL_2_WRR = "ol_2_wrr___"
    # SLSTR
    SL_1_RBT = "sl_1_rbt___"
    SL_2_AOD = "sl_2_aod___"
    SL_2_FRP = "sl_2_frp___"
    SL_2_LST = "sl_2_lst___"
    SL_2_WST = "sl_2_wst___"
    # SRAL
    # SYNERGY
    SY_2_SYN = "sy_2_syn___"
    SY_2_V10 = "sy_2_v10___"
    SY_2_VG1 = "sy_2_vg1___"
    SY_2_VGP = "sy_2_vgp___"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in S3AProdType]


class S3BProdType(Enum):
    UNKNOWN = "unknown"
    SY_2_AOD = "sy_2_aod___"
    OL_1_ERR = "ol_1_err___"
    SL_2_LST = "sl_2_lst___"
    SY_2_VGP = "sy_2_vgp___"
    SY_2_VG1 = "sy_2_vg1___"

    @staticmethod
    def get_all():
        """ Returns array containing all values. """
        return [e.value for e in S3BProdType]
