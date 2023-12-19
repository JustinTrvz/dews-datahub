from datetime import datetime
import os
import logging
from pathlib import Path
from geopy.geocoders import Nominatim

from django.contrib.gis.geos import Polygon
from sat_data.services.path_finder import PathFinder

from sat_data.services.utils.file_utils import FileUtils
from sat_data.enums.sat_mission import SatMission
from sat_data.enums.sat_prod_type import S2BProdType, S3AProdType, S3BProdType
from sat_data.models import AreaInfo, BandInfo, SatData, TimeSeries, remove_media_root
from sat_data.enums.sat_prod_type import S1AProdType


logger = logging.getLogger("django")


class AttrAdder():
    sat_data: SatData = None
    id = None
    mission: str = ""
    product_type: str = ""
    extracted_path: str = ""
    metadata_dict = {}
    img_supported_prod_types = [
        S1AProdType.SLC.value,
        S1AProdType.GRD.value,
        S1AProdType.GRD_COG.value,
    ]
    path_dict = {}

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
        """ Starts the process of adding attributes to SatData object."""
        logger.debug(f"Starting AttrAdder process... sat_data.id='{self.id}'")

        # Set prod type and mission
        self.set_product_type()
        self.set_mission()
        self.set_name()
        logger.debug(f"Set product type and mission. sat_data.id='{self.id}'")

        # Get path dictionary
        logger.debug(f"Calling PathFinder... sat_data.id='{self.id}'")
        path_finder = PathFinder()
        self.path_dict = path_finder.get_path_dict(
            extracted_path=self.extracted_path,
            mission=self.mission,
            product_type=self.sat_data.product_type,
        )
        logger.debug(f"Created path dictionary. sat_data.id='{self.id}'")
        logger.debug(
            f"SatData id: {self.sat_data.id}, Path dict: {self.path_dict}")

        # Set file paths
        self.set_manifest()
        self.set_xfdu_manifest()
        self.set_inspire()
        self.set_eop_metadata()
        self.set_thumbnail()
        self.set_img_paths()
        logger.debug(
            f"Set manifest, xfdu manifest, inspire, eop metadata, thumbnail and img paths. sat_data.id='{self.id}'")

        # Set other info
        self.set_coordinates()
        self.set_capture_info()
        self.set_time_series()

        logger.debug(
            f"Set coordinates, capture info and time series. sat_data.id='{self.id}'")

        # Save operation is executed in views
        logger.debug(f"AttrAdder done! sat_data.id='{self.id}'")
        return
    
    def set_name(self):
        logger.debug(f"Setting name... sat_data.id='{self.id}'")
        self.sat_data.name = os.path.basename(self.sat_data.archive.url).replace(".zip", "")
        logger.debug(f"Set name. sat_data.id='{self.id}', name='{self.sat_data.name}'")

    def set_time_series(self):
        logger.debug(f"Setting time series... sat_data.id='{self.id}'")
        # Check if time series with this mission, product type and coordinates already exists
        logger.debug("Checking if time series already exists...")
        time_series = TimeSeries.objects.filter(
            mission=self.sat_data.mission,
            product_type=self.sat_data.product_type,
            coordinates=self.sat_data.coordinates,
        ).first()

        if time_series:
            # Use existing TimeSeries object as attribute
            logger.debug(
                f"Found TimeSeries object. sat_data.id='{self.id}', time_series='{time_series}'")
            self.sat_data.time_series = time_series
        else:
            # Create new TimeSeries object
            logger.debug(
                f"Create new TimeSeries object. sat_data.id='{self.id}'")
            time_series = TimeSeries(
                mission=self.sat_data.mission,
                product_type=self.sat_data.product_type,
                thumbnail=self.sat_data.thumbnail,
                coordinates=self.sat_data.coordinates,
                leaflet_coordinates=self.sat_data.leaflet_coordinates,
            )
            time_series.save()  # must be saved to db before assignment
            self.sat_data.time_series = time_series

    def set_capture_info(self):
        """ Sets capture info attribte in SatData object."""
        # Check if metadata_dict is empty
        if not self.metadata_dict:
            logger.warn(
                f"Metadata dictionary is empty. sat_data.id='{self.id}'")
            return

        # Identify start and stop time keywords
        if self.mission == SatMission.SENTINEL_1A.value or self.mission == SatMission.SENTINEL_2B.value:
            # Sentinel-1A or Sentinel-2B
            start_time_keyword = "safe:startTime"
            stop_time_keyword = "safe:stopTime"
        elif self.mission == SatMission.SENTINEL_3A.value or self.mission == SatMission.SENTINEL_3B.value:
            # Sentinel-3A or Sentinel-3B
            start_time_keyword = "sentinel-safe:startTime"
            stop_time_keyword = "sentinel-safe:stopTime"

        # Get start and stop time
        logger.debug(f"Getting start and stop time... sat_data.id='{self.id}'")
        start_time = FileUtils.get_dict_value_by_key(
            self.metadata_dict, start_time_keyword)
        stop_time = FileUtils.get_dict_value_by_key(
            self.metadata_dict, stop_time_keyword)
        # Convert to datetime
        logger.debug(
            f"Converting start and stop time to datetime... sat_data.id='{self.id}'")
        start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
        stop_time_dt = datetime.strptime(stop_time, "%Y-%m-%dT%H:%M:%S.%f")
        logger.debug(
            f"Start and stop time as datetime. sat_data.id='{self.id}', start_time='{start_time_dt}', stop_time='{stop_time_dt}'")

        # Get country using Nominatim
        logger.debug(
            f"Getting country using Nominatim... sat_data.id='{self.id}'")
        geolocator = Nominatim(user_agent="dews")
        polygon = self.sat_data.coordinates
        centroid = polygon.centroid
        location = geolocator.reverse(
            (centroid.y, centroid.x), exactly_one=True, language='en')
        if location and 'country' in location.raw['address']:
            logger.debug(
                f"Found country. sat_data.id='{self.id}', country='{location.raw['address']['country']}'")
            country = location.raw['address']['country']
        else:
            logger.debug(f"Could not find country. sat_data.id='{self.id}', polygon='{polygon}', centroid='{centroid}', location='{location}'")
            country = "Unknown"

        # Save SatData object
        try:
            self.sat_data.save()
        except Exception as e:
            logger.error(
                f"Could not save SatData object. sat_data.id='{self.id}', exception='{e}'")
        # Create AreaInfo object
        area_info = AreaInfo(sat_data=self.sat_data,
                             country=country,
                             start_time=start_time_dt,
                             stop_time=stop_time_dt,
                             )
        logger.debug(
            f"Created AreaInfo object. sat_data.id='{self.id}', area_info.sat_data='{area_info.sat_data}'")
        # Set AreaInfo object as attribute to SatData object
        self.sat_data.area_info = area_info
        logger.debug(
            f"Set AreaInfo as attribute to SatData object. sat_data.id='{self.id}', area_info.sat_data='{area_info.sat_data}'")

    def set_coordinates(self):
        """ Sets coordinates attribte in SatData object."""
        logger.debug(f"Setting polygon coordinates... sat_data.id='{self.id}'")
        sat_data = self.sat_data

        if self.product_type in PathFinder.has_manifest_prod_types:
            # Get coordinates from 'manifest.safe' file
            logger.debug(
                f"Identified '{self.mission}' SatData object. id='{sat_data.id}'")
            self.metadata_dict = FileUtils.xml_to_dict(sat_data.manifest.url)
            coordinates = FileUtils.get_dict_value_by_key(
                self.metadata_dict, "gml:coordinates").lower()
            coordinate_pairs = coordinates.split()
            
            # Convert to a tuple of floats (latitude, longitude)
            coordinate_tuples = [tuple(map(float, pair.split(',')))
                                 for pair in coordinate_pairs]
            if coordinate_tuples[0] != coordinate_tuples[-1]:
                coordinate_tuples.append(coordinate_tuples[0])
            logger.debug(
                f"coordinate_tuples='{coordinate_tuples}', sat_data.id='{self.id}'")
            
            # Polygon needs four points
            if len(coordinate_tuples) <= 3:
                logger.warn(
                    f"Not enough points to create a polygon. Need at least 4 points, but got {len(coordinate_tuples)}. sat_data.id='{self.id}', coordinates='{coordinates}'")
                return
            # Set coordinates
            sat_data.coordinates = Polygon(coordinate_tuples)

            # Leaflet needs the reverse order of the coordinates
            reverse_tuples = [(b, a) for a, b in coordinate_tuples]
            sat_data.leaflet_coordinates = Polygon(reverse_tuples)
            logger.debug(
                f"Set Polygon coordinates to SatData object. sat_data.id='{self.id}', coordinates='{coordinates}'")
        else:
            # No coordinates available
            logger.debug(f"No coordinates available. sat_data.id='{self.id}'")

    def set_img_paths(self):
        """ Sets band image paths in SatData object."""
        logger.debug(f"Setting band image paths... sat_data.id='{self.id}'")
        sat_data = self.sat_data
        if not sat_data.product_type in self.img_supported_prod_types:
            logger.info(
                f"Did not add image paths because product type '{sat_data.product_type}' has no image support yet.")
            return

        # List all possible image files in "measurement path"
        logger.debug(
            f"Listing all possible image files in 'measurement' directory. id='{self.id}'")
        img_files = os.listdir(f"{self.extracted_path}/measurement")

        # Generate a list of band substrings
        # ["b-001", "b-002", ...]
        logger.debug("Generate a list of band substrings.")
        bands_substrings = [
            f"b-{str(i).zfill(3)}" for i in range(1, 13)] + ["b-08a", "aot", "scl", "tci", "wvp"]
        logger.debug(f"Band substrings: {bands_substrings}")

        # Iterate through the files and check for substrings
        logger.debug("Create BandInfo object.")
        band_info = BandInfo(sat_data=self.sat_data)
        logger.debug(f"BANDINFO: {band_info}")
        logger.debug(
            f"Iterate through the image files and check for 'b???' substring. id='{self.id}'")
        for file_name in img_files:
            for substring in bands_substrings:
                if substring in file_name:
                    logger.info(
                        f"File '{file_name}' contains the substring '{substring}'.")
                    # Update the model attribute with the full path
                    attr_name = f"b{substring[3:]}"
                    full_path = f"{sat_data.extracted_path}/measurement/{file_name}"
                    logger.debug(f"Full path={full_path}")
                    self.__update_attr(
                        model=band_info,
                        attr_name=attr_name,
                        value=full_path,
                    )
        sat_data.save()
        logger.debug(f"Saved SatData object. sat_data.id='{self.id}'")
        band_info.sat_data = sat_data
        logger.debug(
            f"Set SatData as attribute to BandInfo object... sat_data.id='{self.id}', band_info.sat_data='{band_info.sat_data}'")
        band_info.save()  # must be saved to db before assignment
        logger.debug(
            f"Saved BandInfo object. band_info.sat_data='{band_info.sat_data}'")
        sat_data.band_info = band_info
        logger.debug(
            f"Set BandInfo as attribute to SatData object... sat_data.id='{self.id}', band_info.sat_data='{band_info.sat_data}'")

    def set_manifest(self):
        """ Sets manifest attribte in SatData object."""
        # Set metadata
        logger.debug(f"Setting manifest path... sat_data.id='{self.id}'")
        manifest_path = self.path_dict["manifest"]
        self.sat_data.manifest = remove_media_root(manifest_path)
        logger.info(
            f"Set manifest. id='{self.sat_data.id}', mission='{self.mission}', manifest_path='{manifest_path}'")

    def set_thumbnail(self):
        """ Sets thumbnail attribte in SatData object."""
        logger.debug(f"Setting thumbnail... sat_data.id='{self.id}'")
        thumbnail_path = self.path_dict["thumbnail"]

        if thumbnail_path == "":
            logger.info(
                f"SatData object has no thumbnail image or mission/product type is not supported yet. id='{self.sat_data.id}', mission='{self.mission}'")
        else:
            self.sat_data.thumbnail = thumbnail_path
            logger.info(
                f"Set thumbnail. id='{self.sat_data.id}', mission='{self.mission}', thumbnail_path='{thumbnail_path}'")

    def set_eop_metadata(self):
        """ Sets eop metadata attribte in SatData object."""
        logger.debug(f"Setting eop metadata... sat_data.id='{self.id}'")
        eop_metadata_path = self.path_dict["eop_metadata"]

        if eop_metadata_path == "":
            logger.info(
                f"SatData object has no eop metadata xml or mission/product type is not supported yet. id='{self.sat_data.id}', mission='{self.mission}'")
        else:
            self.sat_data.eop_metadata = eop_metadata_path
            logger.info(
                f"Set eop metadata. id='{self.sat_data.id}', mission='{self.mission}', eop_metadata_path='{eop_metadata_path}'")

    def set_xfdu_manifest(self):
        """ Sets xfdu manifest attribte in SatData object."""
        logger.debug(f"Setting xfdu manifest... sat_data.id='{self.id}'")
        xfdu_manifest_path = self.path_dict["xfdu_manifest"]

        if xfdu_manifest_path == "":
            logger.info(
                f"SatData object has no xfdu manifest xml or mission/product type is not supported yet. id='{self.sat_data.id}', mission='{self.mission}'")
        else:
            self.sat_data.xfdu_manifest = xfdu_manifest_path
            logger.info(
                f"Set xfdu manifest. id='{self.sat_data.id}', mission='{self.mission}', xfdu_manifest_path='{xfdu_manifest_path}'")

    def set_manifest(self):
        """ Sets manifest attribute in SatData object."""
        logger.debug(f"Setting manifest... sat_data.id='{self.id}'")
        manifest_path = self.path_dict["manifest"]

        if manifest_path == "":
            logger.info(
                f"SatData object has no manifest xml or mission/product type is not supported yet. id='{self.sat_data.id}', mission='{self.mission}'")
        else:
            self.sat_data.manifest = manifest_path
            logger.info(
                f"Set manifest. id='{self.sat_data.id}', mission='{self.mission}', manifest_path='{manifest_path}'")

    def set_inspire(self):
        """ Sets inspire attribte in SatData object."""
        logger.debug(f"Setting inspire... sat_data.id='{self.id}'")
        inspire_path = self.path_dict["inspire"]

        if inspire_path == "":
            logger.info(
                f"SatData object has no inspire xml or mission/product type is not supported yet. id='{self.sat_data.id}', mission='{self.mission}'")
        else:
            self.sat_data.inspire = inspire_path
            logger.info(
                f"Set inspire. id='{self.sat_data.id}', mission='{self.mission}', inspire_path='{inspire_path}'")

    def set_mission(self):
        """ Sets mission attribute in SatData object."""
        self.sat_data.mission = self.mission
        logger.info(f"Set mission. id='{self.id}', mission='{self.mission}'")

    def set_product_type(self):
        """ Sets product type attribute in SatData object."""
        logger.debug(f"Setting product type... sat_data.id='{self.id}'")
        sat_data = self.sat_data

        # Method 1: Identify product type by file name

        if self.mission == SatMission.SENTINEL_2B.value:
            logger.debug(
                f"Identifying {self.mission}'s product type by file name... id='{sat_data.id}'")
            # Sentinel-2B
            product_type = self.product_type_by_filename(sat_data)
            if product_type in S2BProdType.get_all():
                logger.debug(
                    f"Extracted '{self.mission}' SatData object's product type '{product_type}'.")
                sat_data.product_type = product_type
                self.product_type = product_type
                logger.info(
                    f"Set product type. id='{sat_data.id}', product_type='{product_type}'")
            else:
                logger.info(
                    f"SatData object has no product type or mission/product type is not supported yet. id='{sat_data.id}', mission='{self.mission}', product_type='{product_type}'")
            return

        # Method 2: Identify product type by metadata
        logger.debug(
            f"Identifying {self.mission}'s product type by metadata... id='{sat_data.id}'")
        product_type = self.product_type_by_metadata(
            self.extracted_path, sat_data)
        logger.debug(S1AProdType.get_all() +
                     S3AProdType.get_all() + S3BProdType.get_all())
        if product_type in S1AProdType.get_all() or product_type in S3AProdType.get_all() or product_type in S3BProdType.get_all():
            logger.debug(
                f"Identified '{self.mission}' SatData object. id='{sat_data.id}'")
            # Sentinel-1A or Sentinel-3A
            logger.debug(
                f"Extracted '{self.mission}' SatData object's product type '{product_type}'.")
            sat_data.product_type = product_type
            self.product_type = product_type
            logger.info(
                f"Set product type. id='{sat_data.id}', product_type='{product_type}'")
        else:
            # Unknown product type
            logger.info(
                f"Extracted product type '{product_type}' which is not supported yet. id='{sat_data.id}', mission='{self.mission}', product_type='{product_type}'")

    def product_type_by_filename(self, sat_data):
        """ 
        Returns product type by metadata filename.

        Returns a string in lowercase.
        """
        # Sentinel-2B
        logger.debug(
            f"Identified '{self.mission}' SatData object. id='{sat_data.id}'")

        # List all files in the extracted path
        files = os.listdir(self.extracted_path)
        # Check if any of the files start with "MTD"
        product_type = S2BProdType.UNKNOWN.value
        for file in files:
            if file.startswith('MTD'):
                # the file has the name MTD_*.xml now extract the * part
                product_type = file.split('_')[1].split('.')[0].lower()
                break
        # returns "unknown" if no metadata was found
        logger.debug(f"Returned product type: '{product_type}'")
        return product_type.lower()

    def product_type_by_metadata(self, extracted_path, sat_data: SatData):
        """
        Returns product type by metadata.

        Returns a string in lowercase.
        """
        # Set keyword to search for in metadata
        if self.mission == SatMission.SENTINEL_1A.value:
            # Sentinel-1A with 'manifest.safe'
            # s1sarl1: <GRD, GRD-COG, SLC>, s1sarl2: <OCN>
            keywords = ["s1sarl1:productType", "s1sarl2:productType"]
            # must set this path manually, as the "manifest" attribute is set later
            metadata_path = f"{extracted_path}/manifest.safe"
            logger.debug(
                f"Using keyword and metadata path for Sentinel-1A. keywords='{keywords}', metadata_path='{metadata_path}'")
        elif self.mission == SatMission.SENTINEL_3A.value or self.mission == SatMission.SENTINEL_3B.value:
            # Sentinel-3A with 'xfdumanifest.xml'
            keywords = ["sentinel3:productType"]
            # must set this path manually, as the "xfdu_manifest" attribute is set later
            metadata_path = f"{extracted_path}/xfdumanifest.xml"
            logger.debug(
                f"Using keyword and metadata path for Sentinel-3A. keywords='{keywords}', metadata_path='{metadata_path}'")
        else:
            logger.info(
                f"SatData object has no product type or mission/product type is not supported yet. id='{sat_data.id}', mission='{self.mission}'")

        logger.debug(
            f"Extracting product type from metadata... sat_data.id='{self.id}'")
        metadata_dict = FileUtils.xml_to_dict(metadata_path)
        
        # Search for product type value in metadata
        for keyword in keywords:
            product_type = FileUtils.get_dict_value_by_key(metadata_dict, keyword)
            if product_type:
                break
    
        logger.debug(f"Returned product type: '{product_type}'")
        if product_type:
            return product_type.lower()
        else:
            # every product type has the "unknown" value, so does not matter which one to use
            return S1AProdType.UNKNOWN.value 

    def __update_attr(self, model, attr_name: str, value: any):
        try:
            setattr(model, attr_name, value)
            logger.info(
                f"Updated attribute '{attr_name}' with value '{value}'")
        except SatData.DoesNotExist:
            logger.error(
                f"Model instance not found for '{attr_name}' and value '{value}'")
