import os
import logging

from sat_data.enums.sat_mission import SatMission
from sat_data.enums.sat_prod_type import S1AProdType, S2BProdType, S3AProdType, S3BProdType
from sat_data.models import remove_media_root


logger = logging.getLogger("django")


class PathFinder():
    extracted_path = ""
    mission = ""
    product_type = ""
    manifest_path = ""
    inspire_path = ""
    xfdu_manifest_path = ""
    eop_metadata_path = ""
    img_metadata_path = ""
    thumbnail_path = ""

    # Manifest
    has_manifest_prod_types = [
        # Sentinel-1A
        S1AProdType.GRD.value,
        S1AProdType.GRD_COG.value,
        S1AProdType.OCN.value,        
        S1AProdType.RAW.value,        
        S1AProdType.SLC.value,
        # Sentinel-2B
        S2BProdType.MSIL1C.value,
        S2BProdType.MSIL2A.value,
        # Sentinel-3A
        S3AProdType.OL_2_WFR.value,
        S3AProdType.OL_2_WRR.value,
        S3AProdType.SL_2_AOD.value,
        S3AProdType.SL_2_FRP.value,
        S3AProdType.SL_2_WST.value,
    ]

    # Inspire
    has_inspire_prod_types = [
        # Sentinel-2B
        S2BProdType.MSIL1C.value,
        S2BProdType.MSIL2A.value,
    ]

    # Xfdu Manifest
    has_xfdu_prod_types = [
        # Sentinel-3B
        S3BProdType.SY_2_AOD.value,
        S3BProdType.OL_1_ERR.value,
        S3BProdType.SL_2_LST.value,
        S3BProdType.SY_2_VGP.value,
        # Sentinel-3A
        S3AProdType.OL_1_ERR.value,
        S3AProdType.OL_2_LFR.value,
        S3AProdType.OL_2_LRR.value,
        S3AProdType.SL_1_RBT.value,
        S3AProdType.SL_2_AOD.value,
        S3AProdType.SL_2_FRP.value,
        S3AProdType.SL_2_LST.value,
        S3AProdType.SL_2_WST.value,
        S3AProdType.SY_2_SYN.value,
        S3AProdType.SY_2_V10.value,
        S3AProdType.SY_2_VG1.value,
        S3AProdType.SY_2_VGP.value,
    ]

    # EOP Metadata
    has_eop_metadata_prod_types = [
        # Sentinel-3A
        S3AProdType.SL_2_AOD.value,
        S3AProdType.SL_2_FRP.value,
        S3AProdType.SL_2_WST.value,
    ]

    # Image Metadata
    has_img_metadata_prod_types = [
        # Sentinel-2B
        S2BProdType.MSIL1C.value,
        S2BProdType.MSIL2A.value,
    ]

    # Thumbnail
    has_quick_look_img_prod_types = [
        # Sentinel-1A
        S1AProdType.GRD.value,
        S1AProdType.GRD_COG.value,
        S1AProdType.SLC.value,
    ]

    has_quicklook_img_prod_types = [
        # Sentinel-3A
        S3AProdType.OL_1_EFR.value,
        S3AProdType.OL_1_ERR.value,
        S3AProdType.OL_2_LFR.value,
        S3AProdType.OL_2_LRR.value,
        S3AProdType.SL_1_RBT.value,
        S3AProdType.SL_2_FRP.value,
        S3AProdType.SL_2_LST.value,
        S3AProdType.SY_2_SYN.value,
        S3AProdType.SY_2_V10.value,
        S3AProdType.SY_2_VG1.value,
        # Sentinel-3B
        S3BProdType.OL_1_ERR.value,
        S3BProdType.SL_2_LST.value,
        S3BProdType.SY_2_VG1.value,
    ]

    has_browse_img_prod_types = [
        S3AProdType.OL_2_WFR.value,
        S3AProdType.OL_2_WRR.value,
        S3AProdType.SL_2_AOD.value,
        S3AProdType.SL_2_FRP.value,
        S3AProdType.SL_2_WST.value,
    ]

    def get_path_dict(self, extracted_path: str, mission: str, product_type: str):
        """ Returns a dictionary containing all paths."""
        # Set attributes
        logger.debug(f"Setting attributes. extracted_path='{extracted_path}', mission='{mission}', product_type='{product_type}'")
        self.extracted_path = extracted_path
        self.mission = mission
        self.product_type = product_type
        self.extracted_path = extracted_path
        self.mission = mission
        self.product_type = product_type

        # Set paths
        logger.debug(f"Setting paths in path dictionary. extracted_path='{self.extracted_path}', mission='{self.mission}', product_type='{self.product_type}'")
        self.__set_manifest_path()
        self.__set_xfdu_manifest_path()
        self.__set_inspire_path()
        self.__set_eop_metadata_path()
        self.__set_img_metadata_path()
        self.__set_thumbnail_path()

        # Create path dict
        logger.debug(f"Return path dictionary. extracted_path='{extracted_path}', mission='{mission}', product_type='{product_type}'")
        return self.create_path_dict()

    def __set_manifest_path(self):
        """ Sets manifest path in a dictionary."""
        # Identify manifest file location
        if self.product_type in self.has_manifest_prod_types:
            logger.debug(f"Product type '{self.product_type}' has manifest xml file.")
            manifest_path = "manifest.safe"
        else:
            logger.debug(f"Product type '{self.product_type}' has no manifest xml file.")
            return

        # Set manifest path
        self.manifest_path = remove_media_root(f"{self.extracted_path}/{manifest_path}")
        return

    def __set_xfdu_manifest_path(self):
        """ Sets xfdu manifest path in a dictionary."""
        if self.product_type in self.has_xfdu_prod_types:
            logger.debug(f"Product type '{self.product_type}' has xfdu manifest xml file.")
            xfdu_manifest_path = "xfdumanifest.xml"
        else:
            logger.debug(f"Product type '{self.product_type}' has no xfdumanifest xml file.")
            return

        # Set xfdu manifest path
        self.xfdu_manifest_path = remove_media_root(f"{self.extracted_path}/{xfdu_manifest_path}")
        return

    def __set_inspire_path(self):
        """ Sets inspire path in a dictionary."""
        if self.product_type in self.has_inspire_prod_types:
            logger.debug(f"Product type '{self.product_type}' has inspire xml file.")
            inspire_path = "INSPIRE.xml"
        else:
            logger.debug(f"Product type '{self.product_type}' has no inspire xml file.")
            return

        # Set inspire path
        self.inspire_path = remove_media_root(f"{self.extracted_path}/{inspire_path}")

    def __set_eop_metadata_path(self):
        """ Sets eop metadata path in a dictionary."""
        if self.product_type in self.has_eop_metadata_prod_types:
            logger.debug(f"Product type '{self.product_type}' has eop metadata xml file.")
            eop_metadata_path = "EOPMetadata.xml"
        else:
            logger.debug(f"Product type '{self.product_type}' has no eop metadata xml file.")
            return
        
        # Set eop metadata path
        self.eop_metadata_path = remove_media_root(f"{self.extracted_path}/{eop_metadata_path}")

    def __set_img_metadata_path(self):
        """ Sets image metadata path in a dictionary."""
        if self.product_type in self.has_img_metadata_prod_types:
            logger.debug(f"Product type '{self.product_type}' has image metadata xml file.")
            img_metadata_path = f"MTD_{self.product_type.upper()}.xml"
        else:
            logger.debug(f"Product type '{self.product_type}' has no image metadata xml file.")
            return

        # Set img metadata path
        self.img_metadata_path = remove_media_root(f"{self.extracted_path}/{img_metadata_path}")

    def __set_thumbnail_path(self):
        """ Sets thumbnail path in a dictionary."""
        if self.product_type == S2BProdType.MSIL1C.value:
            # Custom quick look
            logger.debug(f"Product type '{self.product_type}' has custom quick look image file.")
            archive_name_without_end = os.path.basename(self.extracted_path).split('.')[0]
            thumbnail_path = f"{archive_name_without_end}-ql.jpg"
        if self.product_type == S1AProdType.OCN.value:
            # "quick-look-lw-___.png"
            # owi and rvl available, will use owi
            logger.debug(f"Product type '{self.product_type}' has custom quick look image file.")
            archive_name_without_end = os.path.basename(self.extracted_path).split('.')[0]
            thumbnail_path = f"preview/quick-look-l2-owi.png"
        elif self.product_type in self.has_quick_look_img_prod_types:
            # 'quick-look' image
            logger.debug(f"Product type '{self.product_type}' has 'quick-look.png' image file.")
            thumbnail_path = "preview/quick-look.png"
        elif self.product_type in self.has_quicklook_img_prod_types:
            # 'quicklook' image
            logger.debug(f"Product type '{self.product_type}' has 'quicklook.png' image file.")
            thumbnail_path = "quicklook.jpg"
        elif self.product_type in self.has_browse_img_prod_types:
            # 'browse' image
            logger.debug(f"Product type '{self.product_type}' has 'browse.png' image file.")
            thumbnail_path = "browse.jpg"
        else:
            # No thumbnail
            logger.debug(f"Product type '{self.product_type}' has no thumbnail image file.")
            return

        self.thumbnail_path = remove_media_root(f"{self.extracted_path}/{thumbnail_path}")
        return

    def create_path_dict(self):
        logger.debug(f"Creating path dictionary. mission='{self.mission}', product_type='{self.product_type}'")
        return {
            "extracted_path": self.extracted_path,
            "mission": self.mission,
            "product_type": self.product_type,
            "manifest": self.manifest_path,
            "inspire": self.inspire_path,
            "xfdu_manifest": self.xfdu_manifest_path,
            "eop_metadata": self.eop_metadata_path,
            "img_metadata": self.img_metadata_path,
            "thumbnail": self.thumbnail_path,
        }
