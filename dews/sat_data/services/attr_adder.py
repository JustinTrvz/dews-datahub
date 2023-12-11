import os
import logging
from pathlib import Path

from django.db import models

from sat_data.services.utils.file_utils import FileUtils
from sat_data.enums.sat_mission import SatMission
from sat_data.models import SatData, remove_media_root
from sat_data.enums.sat_prod_type import Sentinel1AProdType

logger = logging.getLogger("django")


class AttrAdder():
    sat_data: SatData = None
    id = None
    mission: str = ""
    extracted_path: str = ""
    img_supported_prod_types = [
        Sentinel1AProdType.SLC.value,
        Sentinel1AProdType.GRD.value,
        Sentinel1AProdType.GRD_COG.value,
    ]

    def __init__(self, sat_data: SatData, extracted_path: str, mission: str) -> None:
        if sat_data is None:
            logger.error(
                f"SatData object is 'None'. extracted_path='{extracted_path}'")
            return
        elif extracted_path == "":
            logger.error(
                f"Extracted path is empty. sat_data.id='{sat_data.id}', mission='{mission}'")
            return
        elif mission == "":
            logger.error(
                f"Mission empty. sat_data.id='{sat_data.id}', extracted_path='{extracted_path}'")
            return
        else:
            logger.debug(
                f"Set SatData variable in AttrAdder object. sat_data='{sat_data}'")
            self.sat_data = sat_data
            self.id = sat_data.id
            self.extracted_path = extracted_path
            self.mission = mission

    def start(self):
        logger.debug(f"Starting AttrAdder process... sat_data.id='{self.id}'")
        self.set_mission()
        self.set_img_paths()
        self.set_metadata()
        self.set_thumbnail()
        self.set_product_type()
        logger.debug(f"AttrAdder done! sat_data.id='{self.id}'")
        try:
            self.sat_data.save()
            logger.info(f"Saved SatData object to database. sat_data.id='{self.sat_data.id}'")
        except Exception as e:
            logger.error(f"Failed to save SatData object to database. sat_data.id='{self.sat_data.id}', error='{e}'")
        return

    def set_img_paths(self):
        logger.debug(f"Setting band image paths... sat_data.id='{self.id}'")
        sat_data = self.sat_data
        if not sat_data.product_type in self.img_supported_prod_types:
            logger.info(
                f"Did not add image paths because product type '{sat_data.product_type}' has no image support yet.")
            return

        # List all possible image files in "measurement path"
        logger.debug(
            f"Listing all possible image files in 'measurement' directory. id='{self.id}'")
        img_files = os.listdir(os.path.join(
            sat_data.extracted_path, "measurement"))

        # Generate a list of band substrings
        # ["b-001", "b-002", ...]
        bands_substrings = [
            f'b-{str(i).zfill(3)}' for i in range(1, 13)] + ['b-08a']

        # Iterate through the files and check for substrings
        logger.debug(
            f"Iterate through the image files and check for 'b???' substring. id='{self.id}'")
        for file_name in img_files:
            for substring in bands_substrings:
                if substring in file_name:
                    logger.info(
                        f"File '{file_name}' contains the substring '{substring}'.")
                    # Update the model attribute with the full path
                    attr_name = f'b{substring[2:]}_path'
                    full_path = os.path.join(
                        sat_data.extracted_path, file_name)
                    self.__update_attr(sat_data.band_info,
                                       attr_name, full_path)

    def set_metadata(self):
        logger.debug(f"Setting metadata path... sat_data.id='{self.id}'")
        sat_data = self.sat_data
        mission = self.sat_data.mission
        if mission == SatMission.SENTINEL_1A.value:
            metadata_path = Path(self.extracted_path) / "manifest.safe"
            sat_data.metadata = remove_media_root(metadata_path)
            logger.info(
                f"Set metadata. id='{sat_data.id}', mission='{mission}', metadata_path='{metadata_path}'")
        else:
            logger.info(
                f"SatData object has no metadata xml file or mission is not supported yet. id='{sat_data.id}', mission='{mission}'")

    def set_thumbnail(self):
        logger.debug(f"Setting thumbnail... sat_data.id='{self.id}'")
        sat_data = self.sat_data
        if self.mission == SatMission.SENTINEL_1A.value:
            thumbnail_path = Path(self.extracted_path) / "preview/thumbnail.png"
            sat_data.thumbnail = remove_media_root(thumbnail_path)
            logger.info(
                f"Set thumbnail. id='{sat_data.id}', mission='{self.mission}', thumbnail_path='{thumbnail_path}'")
        else:
            logger.info(
                f"SatData object has no thumbnail image or mission is not supported yet. id='{sat_data.id}', mission='{self.mission}'")

    def set_mission(self):
        self.sat_data.mission = self.mission
        logger.info(f"Set mission. id='{self.id}', mission='{self.mission}'")

    def set_product_type(self):
        logger.debug(f"Setting product type... sat_data.id='{self.id}'")
        sat_data = self.sat_data
        if self.mission == SatMission.SENTINEL_1A.value:
            logger.debug(
                f"Identified '{self.mission}' SatData object. id='{sat_data.id}'")
            metadata_dict = FileUtils.xml_to_dict(sat_data.metadata.url)
            product_type = FileUtils.get_dict_value_by_key(metadata_dict, "s1sarl1:productType")
            logger.debug(
                f"Extracted '{self.mission}' SatData object's product type '{product_type}'.")
            sat_data.product_type = product_type
            logger.info(
                f"Set product type. id='{sat_data.id}', product_type='{product_type}'")
        else:
            logger.info(
                f"SatData object has no product type or mission is not supported yet. id='{sat_data.id}', mission='{self.mission}'")

    def __update_attr(self, model: models.Model, attr_name: str, value: any):
        try:
            setattr(model, attr_name, value)
            logger.info(
                f"Updated '{attr_name}' for {model}. value='{value}'")
        except SatData.DoesNotExist:
            logger.error(
                f"Model instance '{model}' not found for '{attr_name}'")
