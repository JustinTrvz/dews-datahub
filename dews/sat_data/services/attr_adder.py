from datetime import datetime
import json
from multiprocessing import Process
import re
import os
import logging
import threading
from geopy.geocoders import Nominatim
import subprocess

from django.contrib.gis.geos import Polygon
from django.contrib.gis.gdal import GDALRaster
from dews.settings import DB_HOST, DB_NAME, DB_PORT, DB_USER, DB_PASSWORD

from sat_data.services.path_finder import PathFinder
from sat_data.services.utils.file_utils import FileUtils
from sat_data.services.utils.dataset_utils import get_dataset
import sat_data.services.metrics_calc as mc
from sat_data.enums.sat_mission import SatMission
from sat_data.enums.sat_prod_type import S2BProdType, S3AProdType, S3BProdType
from sat_data.models import Area, Band, SatData, TimeTravel, remove_media_root
from sat_data.enums.sat_prod_type import S1AProdType, S2AProdType, S2BProdType
from dews.settings import MEDIA_ROOT


logger = logging.getLogger("django")


class AttrAdder():
    sat_data: SatData = None
    id = None
    mission: str = ""
    product_type: str = ""
    extracted_path: str = ""
    extracted_abs_path: str = ""
    metadata_dict = {}

    # Sentinel Hub Request specific
    sh_request = False
    bbox = None
    bands = None
    bands_paths = {}

    # Product types
    tiff_file_prod_types = [
        S1AProdType.SLC.value,
        S1AProdType.GRD.value,
        S1AProdType.GRD_COG.value,
    ]
    jp2_file_prod_types = [
        S2AProdType.S2MSI1C.value,
        S2AProdType.S2MSI2A.value,
        S2BProdType.S2MSI1C.value,
        S2BProdType.S2MSI2A.value,
    ]
    nc_file_prod_types = [

    ]
    path_dict = {}

    def __init__(self, sat_data: SatData, extracted_path: str, mission: str, sh_request=False, bbox=None, bands=None, date=None) -> None:
        logger.debug("AttrAdder object created.")
        # Set processing status
        sat_data.processing_done = False
        logger.debug(
            f"Set processing status to '{sat_data.processing_done}'. sat_data.id='{sat_data.id}'")
        sat_data.save()

        if sat_data is None:
            logger.error(
                f"SatData object is 'None'. extracted_path='{extracted_path}'")
            return
        elif extracted_path == "":
            logger.error(
                f"Extracted path is empty. sat_data.id='{sat_data.id}', sat_data.mission='{mission}'")
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
            if MEDIA_ROOT in extracted_path:
                self.extracted_abs_path = extracted_path
            else:
                self.extracted_abs_path = FileUtils.generate_path(MEDIA_ROOT, extracted_path)
            logger.debug(f"Extracted absolute path: {self.extracted_abs_path}")
            self.mission = mission
            self.sh_request = sh_request
            self.bbox = bbox
            self.bands = bands
            self.date = date
            logger.debug(
                f"Set AttrAdder class variables. sat_data.id='{self.id}'")

    def start(self):
        """ Starts the process of adding attributes to SatData object."""
        logger.debug(f"Starting AttrAdder process... sat_data.id='{self.id}'")
        # Set prod type and mission
        self.set_product_type()
        self.set_extracted_path()
        self.set_mission()
        self.set_name()
        logger.debug(f"Set product type and mission. sat_data.id='{self.id}'")

        if not self.sh_request:
            # Get path dictionary (only for archives!)
            logger.debug(f"Calling PathFinder... sat_data.id='{self.id}'")
            path_finder = PathFinder()
            self.path_dict = path_finder.get_path_dict(
                extracted_path=self.extracted_abs_path,
                mission=self.mission,
                product_type=self.sat_data.product_type,
            )
            logger.debug(f"Created path dictionary. sat_data.id='{self.id}'")
            logger.debug(
                f"SatData id: {self.sat_data.id}, Path dict: {self.path_dict}")

            # Set file paths
            self.set_mtd()
            self.set_manifest()
            self.set_xfdu_manifest()
            self.set_inspire()
            self.set_eop_metadata()
            logger.debug(
                f"Set manifest, xfdu manifest, inspire, eop metadata and img paths. sat_data.id='{self.id}'")
        else:
            # Sentinel Hub Request
            logger.debug(
                f"Check if `response.tar` exists... sat_data.id='{self.id}', extracted_path='{self.extracted_path}'")
            tar_path = FileUtils.generate_path(
                self.extracted_abs_path, "response.tar")
            self.check_for_tar_file(tar_path)

        self.set_thumbnail()
        logger.debug(
            f"Set thumbnail. sat_data.id='{self.id}', sat_data.thumbnail='{self.sat_data.thumbnail}'")

        # Set other info
        self.set_coordinates()
        self.set_area_details()
        self.set_time_series()

        logger.debug(
            f"Set coordinates, capture info/area details and time series. sat_data.id='{self.id}'")

        # Long time consuming process:
        self.set_bands()
        logger.debug(f"Set bands. sat_data.id='{self.id}'")

        # Metrics calculation
        # self.metrics_calculation()
        # logger.debug(f"Metrics calculation done. sat_data.id='{self.id}'")

        # Save operation is executed in views
        logger.debug(f"AttrAdder done! sat_data.id='{self.id}'")

        # Set processing status
        self.sat_data.processing_done = True
        logger.debug(
            f"Set processing status to '{self.sat_data.processing_done}'. sat_data.id='{self.id}'")
        # Save SatData object
        logger.debug(f"Execute final save. sat_data.id='{self.id}'")
        self.sat_data.save()

    def check_for_tar_file(self, tar_path):
        if os.path.exists(tar_path):
            # Extract `response.tar`
            logger.debug(
                f"Extracting `response.tar`... sat_data.id='{self.id}'")
            extract_path = FileUtils.extract_tar(
                tar_path=tar_path,
                extract_path=self.extracted_abs_path,
            )
            logger.debug(
                f"Extracted `response.tar` to `{extract_path}`. sat_data.id='{self.id}'")
        else:
            logger.debug(
                f"`response.tar` does not exist. sat_data.id='{self.id}'")

    def set_extracted_path(self):
        """ Sets extracted path attribte in SatData object."""
        logger.debug(f"Setting extracted path... sat_data.id='{self.id}'")
        self.sat_data.extracted_path = remove_media_root(self.extracted_path)
        logger.debug(
            f"Set extracted path. sat_data.id='{self.id}', extracted_path='{self.extracted_path}'")

    def metrics_calculation(self):
        logger.debug(f"Calculating metrics... sat_data.id='{self.id}'")

        metrics_calculator = mc.MetricsCalculator(
            sat_data=self.sat_data,
            bands_paths=self.bands_paths,
            metrics_to_calc=["ndvi", "smi", "rgb"])  # TODO: given by user
        process = Process(target=metrics_calculator.start, args=(self,))
        logger.debug(
            f"Starting metrics calculation process... sat_data.id='{self.id}'")
        process.start()

        # # Calculate NDVI
        # if "B04" in self.bands and "B08" in self.bands:
        #     logger.debug(f"Calculate NDVI. sat_data.id='{self.id}', image_path_04='{self.bands_paths['b04']}', image_path_08='{self.bands_paths['b08']}'")
        #     mc.calculate_ndvi(
        #         sat_data=self.sat_data,
        #         image_path_04=self.bands_paths["b04"],
        #         image_path_08=self.bands_paths["b08"],
        #         save_location=FileUtils.generate_path(
        #             self.extracted_abs_path),
        #     )
        # # Calculate SMI
        # if "B8A" in self.bands and "B11" in self.bands:
        #     mc.calculate_smi(
        #         sat_data=self.sat_data,
        #         image_path_8a=self.bands_paths["b8a"],
        #         image_path_11=self.bands_paths["b11"],
        #         save_location=FileUtils.generate_path(
        #             self.extracted_abs_path),
        #     )

    def set_mtd(self):
        """ Sets mtd attribte in SatData object."""
        logger.debug(f"Setting mtd ... sat_data.id='{self.id}'")
        mtd_path = self.path_dict["mtd"]

        if mtd_path == "":
            logger.info(
                f"SatData object has no 'MTD_*.xml' or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")
        else:
            self.sat_data.mtd = mtd_path
            logger.info(
                f"Set mtd. sat_data.id='{self.id}', sat_data.mission='{self.mission}', mtd_path='{mtd_path}'")

    def set_name(self):
        logger.debug(f"Setting name... sat_data.id='{self.id}'")

        if self.sh_request:
            # Sentinel Hub Request
            self.sat_data.name = f"Sentinel Hub Request {self.sat_data.id}"
        else:
            # Archive upload
            self.sat_data.name = os.path.basename(
                self.sat_data.archive.url).replace(".zip", "")

        logger.debug(
            f"Set name. sat_data.id='{self.id}', name='{self.sat_data.name}'")

    def set_time_series(self):
        logger.debug(f"Setting time series... sat_data.id='{self.id}'")

        # Check if time series with this mission, product type and coordinates already exists
        logger.debug("Checking if time series already exists...")
        time_series = TimeTravel.objects.filter(
            mission=self.sat_data.mission,
            product_type=self.sat_data.product_type,
            coordinates=self.sat_data.coordinates,
        ).first()

        if time_series:
            # Use existing TimeSeries object as attribute
            logger.debug(
                f"Found TimeSeries object. sat_data.id='{self.id}', time_series='{time_series}'")
            self.sat_data.time_travels = time_series
        else:
            # Create new TimeSeries object
            logger.debug(
                f"Create new TimeSeries object. sat_data.id='{self.id}'")
            time_series = TimeTravel(
                mission=self.sat_data.mission,
                product_type=self.sat_data.product_type,
                thumbnail=self.sat_data.thumbnail,
                coordinates=self.sat_data.coordinates,
                leaflet_coordinates=self.sat_data.leaflet_coordinates,
            )
            time_series.save()  # must be saved to db before assignment
            self.sat_data.time_travels = time_series

    def set_area_details(self):
        """ Create Area objects and appens it to the related SatData object."""
        logger.debug(f"Setting capture info... sat_data.id='{self.id}'")

        # Sentinel Hub Request
        if self.sh_request:
            start_time_dt = self.date
            stop_time_dt = self.date
            logger.debug(f"Set start and stop time. sat_data.id='{self.id}'")
        else:
            # Archive upload
            # Check if metadata_dict is empty
            if not self.metadata_dict:
                logger.warn(
                    f"Metadata dictionary is empty. sat_data.id='{self.id}'")
                return

            start_time_keyword = ""
            stop_time_keyword = ""
            # Identify start and stop time keywords and datetime format
            dt_format = "%Y-%m-%dT%H:%M:%S.%f"
            if self.mission in [SatMission.SENTINEL_1A.value, SatMission.SENTINEL_2A.value, SatMission.SENTINEL_2B.value]:
                # Sentinel-1A or Sentinel-2B
                start_time_keyword = "safe:startTime"
                stop_time_keyword = "safe:stopTime"
                if self.mission in [SatMission.SENTINEL_2A.value, SatMission.SENTINEL_2B.value]:
                    dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"

            elif self.mission in [SatMission.SENTINEL_3A.value, SatMission.SENTINEL_3B.value]:
                # Sentinel-3A or Sentinel-3B
                start_time_keyword = "sentinel-safe:startTime"
                stop_time_keyword = "sentinel-safe:stopTime"

            # Get start and stop time
            if start_time_keyword == "" and stop_time_keyword == "":
                start_time_dt, stop_time_dt = None
            else:
                logger.debug(
                    f"Getting start and stop time... sat_data.id='{self.id}'")
                start_time_dt, stop_time_dt = self.get_start_and_stop_time(
                    dt_format, start_time_keyword, stop_time_keyword)

        # Get country using Nominatim
        logger.debug(
            f"Getting country using Nominatim... sat_data.id='{self.id}'")
        country = self.get_country()

        # Save SatData object
        try:
            self.sat_data.save()
        except Exception as e:
            logger.error(
                f"Could not save SatData object. sat_data.id='{self.id}', exception='{e}'")
        # Create AreaInfo object
        area = Area(sat_data=self.sat_data,
                         country=country,
                         start_time=start_time_dt,
                         stop_time=stop_time_dt,
                         )
        logger.debug(
            f"Created AreaInfo object. sat_data.id='{self.id}', area.sat_data='{area.sat_data}'")
        # Set AreaInfo object as attribute to SatData object
        self.sat_data.area = area
        logger.debug(f"Set AreaInfo object as attribute to SatData object. sat_data.id='{self.id}'")
        self.sat_data.save()
        logger.debug(f"Saved SatData object. sat_data.id='{self.id}'")
        area.sat_data = self.sat_data
        logger.debug(f"Set SatData object as attribute to AreaInfo object. sat_data.id='{self.id}'")
        area.save()
        logger.debug(f"Saved AreaInfo object. sat_data.id='{self.id}'")
        
    def get_start_and_stop_time(self, format, start_time_keyword, stop_time_keyword):
        logger.debug(
            f"format='{format}', start_time_keyword='{start_time_keyword}', stop_time_keyword='{stop_time_keyword}'")

        start_time = FileUtils.get_dict_value_by_key(
            self.metadata_dict, start_time_keyword)
        stop_time = FileUtils.get_dict_value_by_key(
            self.metadata_dict, stop_time_keyword)
        # Convert to datetime
        logger.debug(
            f"Converting start and stop time to datetime... sat_data.id='{self.id}'")
        if start_time:
            start_time_dt = datetime.strptime(start_time, format)
        else:
            logger.debug(
                f"Could not convert start time to datetime. sat_data.id='{self.id}', start_time_keyword='{start_time_keyword}', stop_time_keyword='{stop_time_keyword}', start_time='{start_time}', stop_time='{stop_time}', format='{format}'")
            start_time_dt = None

        if stop_time:
            stop_time_dt = datetime.strptime(stop_time, format)
        else:
            logger.debug(
                f"Could not convert stop time to datetime. sat_data.id='{self.id}', start_time_keyword='{start_time_keyword}', stop_time_keyword='{stop_time_keyword}', start_time='{start_time}', stop_time='{stop_time}', format='{format}'")
            stop_time_dt = None

        logger.debug(
            f"Start and stop time as datetime. sat_data.id='{self.id}', start_time='{start_time_dt}', stop_time='{stop_time_dt}'")
        return start_time_dt, stop_time_dt

    def get_country(self):
        geolocator = Nominatim(user_agent="dews")
        polygon = self.sat_data.coordinates
        centroid = polygon.centroid
        location = geolocator.reverse(
            (centroid.y, centroid.x), exactly_one=True, language='en')
        if location and location.raw["address"]:
            logger.debug(f"Location and location.raw['address'] available.")
            if "country" in location.raw['address']:
                logger.debug(
                    f"Found country. sat_data.id='{self.id}', country='{location.raw['address']['country']}'")
                country = location.raw['address']['country']
        else:
            logger.debug(
                f"Could not find country. sat_data.id='{self.id}', polygon='{polygon}', centroid='{centroid}', location='{location}'")
            country = "Unknown"
        return country

    def set_coordinates(self):
        """ Sets coordinates attribte in SatData object."""
        logger.debug(f"Setting polygon coordinates... sat_data.id='{self.id}'")
        sat_data = self.sat_data

        coordinate_tuples = []
        if self.sh_request:
            # Sentinel Hub Request

            coords = list(map(float, self.bbox.split(',')))
            coordinate_tuples = [
                (coords[0], coords[1]),  # Bottom-left
                (coords[0], coords[3]),  # Top-left
                (coords[2], coords[3]),  # Top-right
                (coords[2], coords[1]),  # Bottom-right
                (coords[0], coords[1])   # Close the polygon by repeating the first point (bottom-left)
            ]
        else:
            # Archive upload
            if self.product_type in PathFinder.has_manifest_prod_types:
                # Get coordinates from 'manifest.safe' file
                logger.debug(
                    f"Identified '{self.mission}' SatData object. sat_data.id='{sat_data.id}'")
                # manifest_path = FileUtils.generate_path(MEDIA_ROOT, sat_data.manifest.url)
                manifest_path = sat_data.manifest.url
                if os.path.exists(manifest_path):
                    # Manifest XML to dictionary
                    self.metadata_dict = FileUtils.xml_to_dict(manifest_path)
                    if not self.metadata_dict:
                        logger.warn(
                            f"Metadata dictionary is empty or could not be read. sat_data.id='{self.id}', manifest_path='{manifest_path}'")
                        return
                else:
                    # Manifest file does not exist
                    logger.warn(
                        f"Manifest file does not exist. sat_data.id='{self.id}', manifest_path='{manifest_path}'")
                    return

                # Extract coordinates from metadata dictionary
                coordinates = FileUtils.get_dict_value_by_key(
                    self.metadata_dict, "gml:coordinates")

                if not coordinates:
                    # Error:
                    logger.warn(
                        f"No coordinates available. sat_data.id='{self.id}'")
                    return
                elif isinstance(coordinates, list):
                    # Coordinates list
                    logger.debug(
                        f"Coordinates list available. sat_data.id='{self.id}'")
                    coordinates = coordinates[0]

                coordinates_splitted = coordinates.split()
                if "," in coordinates:
                    # Comma seperated coordinates
                    logger.debug(
                        f"Coordinates are comma seperated. coordinates='{coordinates}', sat_data.id='{self.id}'")
                    coordinate_tuples = [tuple(map(float, pair.split(',')))
                                         for pair in coordinates_splitted]
                else:
                    # Space seperated coordinates
                    logger.debug(
                        f"Coordinates are space seperated. coordinates='{coordinates}', sat_data.id='{self.id}'")
                    coordinate_tuples = [(float(coordinates_splitted[i]), float(coordinates_splitted[i + 1]))
                                         for i in range(0, len(coordinates_splitted), 2)]

                if coordinate_tuples[0] != coordinate_tuples[-1]:
                    coordinate_tuples.append(coordinate_tuples[0])
            else:
                # No coordinates available
                logger.warn(
                    f"No coordinates available. sat_data.id='{self.id}'")

        # Set coordinates
        logger.debug(
            f"coordinate_tuples='{coordinate_tuples}', sat_data.id='{self.id}', product_type='{self.product_type}', sat_data.mission='{self.mission}'")
        # Polygon needs four points
        if len(coordinate_tuples) <= 3:
            logger.warn(
                f"Not enough points to create a polygon. Need at least 4 points, but got {len(coordinate_tuples)}. sat_data.id='{self.id}', coordinates_tuples='{coordinate_tuples}'")
            return
        # Set coordinates
        sat_data.coordinates = Polygon(coordinate_tuples)

        # Leaflet needs the reverse order of the coordinates
        reverse_tuples = [(b, a) for a, b in coordinate_tuples]
        sat_data.leaflet_coordinates = Polygon(reverse_tuples)
        logger.debug(
            f"Set Polygon coordinates to SatData object. sat_data.id='{self.id}', coordinate_tuples='{coordinate_tuples}'")

    def set_bands(self):
        """ Sets bands in SatData object."""
        logger.debug(f"Setting bands... sat_data.id='{self.id}'")
        sat_data = self.sat_data

        if self.sh_request:
            # Sentinel Hub Request
            # Get TIFF file path
            tiff_path = ""
            # if .tar exists
            default_tif_path = FileUtils.generate_path(
                self.extracted_abs_path, "default.tif")
            response_tif_path = FileUtils.generate_path(
                self.extracted_abs_path, "response.tif")
            if os.path.exists(default_tif_path):
                # if `response.tar` exists
                tiff_path = default_tif_path
            elif os.path.exists(response_tif_path):
                # no `response.tar` file
                tiff_path = response_tif_path
            else:
                logger.debug(
                    f"Could not split TIFF file into seperate bands because no TIFF file found. sat_data.id='{self.id}', extracted_abs_path='{self.extracted_abs_path}', default_tif_path='{default_tif_path}', response_tif_path='{response_tif_path}', response_tif_path='{response_tif_path}'")
                return

            # Split TIFF file into seperate bands
            if tiff_path:
                logger.debug(
                    f"Split TIFF file into seperate bands. sat_data.id='{self.id}'")
                self.bands_paths = FileUtils.split_tiff(self.bands, tiff_path)
            else:
                logger.debug(
                    f"Could not split TIFF file into seperate bands because no TIFF path defined. sat_data.id='{self.id}'")

        # Archive upload
        if sat_data.product_type in self.tiff_file_prod_types or \
                self.sh_request:  # Sentinel Hub Request's default
            # TIFF files
            if self.sh_request:
                logger.debug(f"Sentinel Hub Request has tiff file bands.")
            else:
                logger.debug(
                    f"Product type '{sat_data.product_type}' has tiff file bands.")
            self.__set_tiff_bands(sat_data)
        elif sat_data.product_type in self.jp2_file_prod_types:
            # JP2 files
            logger.debug(
                f"Product type '{sat_data.product_type}' has jp2 file bands.")
            self.__set_jp2_bands(sat_data)

        # Check if extracted path contains .nc files
        if self.contains_file_by_ext(self.extracted_abs_path, ".nc"):
            logger.debug(
                f"Product type '{sat_data.product_type}' has '.nc' files.")
            self.__set_nc_bands(sat_data)
        else:
            # No bands available
            logger.info(
                f"No '.nc' files found. sat_data.id='{self.id}'.")

        logger.debug(
            f"Set bands to SatData object done. sat_data.id='{self.id}'")

    def contains_file_by_ext(self, directory, ext):
        # Check if the directory contains any .nc files
        if not MEDIA_ROOT in directory:
            directory = FileUtils.generate_path(MEDIA_ROOT, directory)
        for filename in os.listdir(directory):
            if filename.endswith(ext):
                return True
        return False

    def get_file_paths_by_ext(self, directory, ext):
        nc_files = []
        for filename in os.listdir(directory):
            if filename.endswith(ext):
                full_path = os.path.join(directory, filename)
                nc_files.append(full_path)
        return nc_files

    def __set_nc_bands(self, sat_data: SatData):
        # List all possible bands in extracted path
        logger.debug(
            f"Listing all possible bands in 'extracted_path' directory. sat_data.id='{self.id}'")

        # Get all .nc file paths
        nc_paths = self.get_file_paths_by_ext(self.extracted_abs_path, ".nc")

        # Convert band to raster and import to database
        logger.debug(f"Convert and add bands... sat_data.id='{self.id}'")
        self.convert_and_add_bands(sat_data, nc_paths, [".nc"])
        logger.debug(
            f"Successfully converting and adding bands done. sat_data.id='{self.id}'")

    def __set_jp2_bands(self, sat_data: SatData):
        # List all possible bands in "IMG_DATA" path
        logger.debug(
            f"Listing all possible bands in '{self.extracted_abs_path}/IMG_DATA' directory. sat_data.id='{self.id}'")

        # Get all .jp2 file paths
        # MTD path already contains the `extracted_path`
        mtd_path = FileUtils.generate_path(MEDIA_ROOT, self.path_dict["mtd"])
        logger.debug(f"MTD Path: {mtd_path}")
        mtd_dict = FileUtils.xml_to_dict(mtd_path)
        jp2_paths = FileUtils.get_all_dict_values_by_key(
            mtd_dict, "IMAGE_FILE")
        logger.debug(f"jp2_paths: {jp2_paths}")
        logger.debug(f"extracted_abs_path: {self.extracted_abs_path}")
        # add extracted path and extension
        jp2_paths = [FileUtils.generate_path(
            self.extracted_abs_path, file_path) + ".jp2" for file_path in jp2_paths]

        # Band sub strings (B01, B02, ..., B8A, B09, ...)
        bands_strings = [f"B{str(i).zfill(2)}" if i != 8 else "B8A" for i in range(
            1, 13)] + ["AOT", "TCI", "WVP", "SCL"]
        sat_data.save()

        # Convert band to raster and import to database

        self.convert_and_add_bands(sat_data, jp2_paths, bands_strings)
        logger.debug(
            f"Successfully converting and adding bands done. sat_data.id='{self.id}'")

    def convert_and_add_bands(self, sat_data: SatData, band_paths, bands_strings):
        logger.debug(f"Convert and add bands... sat_data.id='{self.id}'")

        sat_data.band_tables = {
            "unknown": [],
            "r10m": [],
            "r20m": [],
            "r60m": [],
        }
        logger.debug(
            f"Set empty 'bands' and 'band_tables' variables. sat_data.id='{self.id}'")
        sat_data.save()
        logger.debug(f"Saved SatData object. sat_data.id='{self.id}'")

        # Check input
        if len(band_paths) == 0:
            logger.warn(
                f"Empty 'band_paths' array passed. sat_data.id='{self.id}'")
            return
        if len(bands_strings) == 0:
            logger.warn(
                f"Empty 'bands_strings' array passed. sat_data.id='{self.id}'")
            return

        for band_path in band_paths:
            for band_string in bands_strings:
                if band_string in band_path:
                    logger.info(
                        f"File '{band_path}' contains the band string '{band_string}'.")

                    # Split band path to search for range part
                    band_path_splitted = band_path.split("/")
                    range_string = "unknown"

                    # Get range string
                    logger.debug(f"Getting range string... sat_data.id='{self.id}'")
                    range_string = self.get_range_string(band_path, band_path_splitted)

                    # Get file name if .nc file
                    if band_string == ".nc":
                        band_string = band_path_splitted[-1]

                    # Shorten mission name
                    logger.debug(f"Shortening mission name... sat_data.id='{self.id}'")
                    mission = sat_data.mission
                    if "-" in mission:
                        mission_split = mission.split("-")
                        mission = f"{mission_split[0][0]}{mission_split[1]}"

                    # Create and import table (as raster) to database
                    logger.debug(f"Creating and importing table... sat_data.id='{self.id}'")
                    table_name = self.import_raster_and_create_table(
                        sat_data=sat_data,
                        mission=mission,
                        band_path=band_path,
                        band_string=band_string,
                        range_string=range_string,
                    )

                    # Create Band object
                    logger.debug(f"Creating Band object... sat_data.id='{self.id}'")
                    ok = self.create_band_obj(
                        band_path=band_path,
                        band_string=band_string,
                        range_string=range_string,
                    )
                    if not ok:
                        logger.error(
                            f"Could not create Band instance. sat_data.id='{self.id}', table_name='{table_name}'")

                    # Append table name to band_tables JSONField
                    if range_string in sat_data.band_tables:
                        # Append to existing array
                        sat_data.band_tables[range_string].append(table_name)
                        sat_data.save()
                        logger.debug(
                            f"Appended table name to existing array '{range_string}' in JSONField 'band_tables'. sat_data.id='{self.id}', table_name='{table_name}'")
                    else:
                        logger.info(
                            f"Range string not found in band_tables. sat_data.id='{self.id}', range_string='{range_string}'")

        # Append table names to SatData object's band_tables array
        # sat_data.band_tables = band_tables
        sat_data.processing_done = True
        sat_data.save()
        logger.debug(
            f"Appended table names to SatData object's band_tables array. sat_data.id='{self.id}'")

    def create_band_obj(self, band_path, band_string, range_string):
        try:
            # Ensure self.sat_data is not None and it's saved
            if self.sat_data and self.sat_data.pk:
                logger.debug(
                    f"SatData instance is valid and saved. sat_data.id='{self.id}'")
            else:
                logger.error(
                    f"SatData instance is either 'None' or not saved. sat_data.id='{self.id}'")
                return

            # Create Band object
            band: Band = Band.objects.create(
                range=int(re.search(r'\d+', range_string).group()),
                type=band_string,
                sat_data=self.sat_data,
            )

            # Save band image and set to Band object
            # band_path_full = FileUtils.generate_path(self.sat_data.extracted_path, band_path)
            save_path = FileUtils.generate_path(
                "sentinel_hub/uploads", f"{self.sat_data.id}_{band_string}_{range_string}.tif")
            with open(band_path, "rb") as img_file:
                band.band_file.save(save_path, img_file)

            # Save Band object
            band.save()
            # Ensure self.sat_data is not 'None' and it's saved
            if self.sat_data and self.sat_data.pk:
                logger.debug(
                    f"Band instance is valid and saved. band.id='{band.id}'")
                if band.sat_data.id != self.sat_data.id:
                    # Error: no relation between Band and SatData
                    logger.error(
                        f"Band instance is not related to SatData instance. band.id='{band.id}', sat_data.id='{self.id}'")
                    return False
                # Relation between Band and SatData is valid
                logger.debug(
                    f"Band instance is related to SatData instance. band.id='{band.id}', sat_data.id='{self.id}'")
                return True
            else:
                # Error: Band instance is 'None' or not saved
                logger.error(
                    f"Band instance is either 'None' or not saved. band.id='{band.id}'")
                return False

        except Exception as e:
            logger.error(
                f"Could not create Band object. sat_data.id='{self.id}', error='{e}'")
            return False

    def import_raster_and_create_table(self, mission: str, sat_data: SatData, band_path, band_string, range_string):
        table_name = f"{mission}_{sat_data.id}_{band_string}".lower()
        # pgsql options
        # -I: Create spatial index
        # -C: Apply raster constraints
        # -F: Add a column with the filename
        # -t auto: Automatically chooses a suitable tile size based on the input raster’s dimensions
        import_cmd = f"raster2pgsql -I -C -F -t auto '{band_path}' public.{table_name} | psql -U {DB_USER} -d {DB_NAME} -h {DB_HOST} -p {DB_PORT}"
        logger.debug(f"table_name: {table_name}")
        logger.debug(f"import_cmd: {import_cmd}")

        # Using environment variables for credentials
        env_vars = {
            "PGPASSWORD": DB_PASSWORD
        }

        # Executing the command
        try:
            subprocess.check_output(
                import_cmd, shell=True, env=env_vars)
        except Exception as e:
            logger.error(
                f"Failed to import raster. error='{e}', band_string='{band_string}', range_string='{range_string}', band_path='{band_path}'")
            return

        logger.info(
            f"Successfully imported raster. band_string='{band_string}', table_name='{table_name}', band_path='{band_path}'")
        return table_name

    def get_range_string(self, band_path, band_path_splitted):
        range_string = "unknown"
        if self.sh_request:
            # Sentinel Hub Request
            range_string = "r20m"
            logger.debug(
                f"Sentinel Hub Request has range '{range_string}'. band_path='{band_path}', range_string='{range_string}'")
        elif len(band_path_splitted) > 2 and not self.sh_request:
            # Archive
            range_part = band_path_splitted[-2]
            match = re.search(r"R\d+m", range_part)
            if match:
                range_string = match.group(0).lower()
                logger.debug(
                    f"Added range part to substring. band_path='{band_path}', range_string='{range_string}'")
            else:
                logger.debug(
                    f"Could not find range part in band path. band_path='{band_path}', range_string='{range_string}'")
        else:
            # Failed to find range part...
            logger.debug(
                f"Could not find range part in band path. band_path='{band_path}', range_string='{range_string}'")

        return range_string

    def __set_tiff_bands(self, sat_data):
        # List all possible bands
        if self.sh_request:
            # Sentinel Hub Request
            logger.debug(
                f"Listing all possible bands in '{self.extracted_abs_path}' directory. sat_data.id='{self.id}'")
            exclude_files = ['response.tif', 'default.tif']
            tiff_paths = [FileUtils.generate_path(self.extracted_abs_path, file) for file in os.listdir(self.extracted_abs_path)
                          if file.endswith('.tif') and file not in exclude_files]
        else:
            # Archive upload
            logger.debug(
                f"Listing all possible bands in '{self.extracted_abs_path}/measurement' directory. sat_data.id='{self.id}'")
            measurement_path = FileUtils.generate_path(
                self.extracted_abs_path, "measurement")
            tiff_paths = os.listdir(measurement_path)

        # Generate a list of band strings
        # ["b-001", "b-002", ...]
        logger.debug("Generate a list of band strings.")
        bands_strings = [f"b-{str(i).zfill(3)}" for i in range(1, 13)] + \
            [f"b{str(i).zfill(2)}" for i in range(1, 13)] + \
            ["b8a", "b-08a", "aot", "scl", "tci", "wvp"]
        logger.debug(f"Band strings: {bands_strings}")

        # Convert band to raster and import to database
        logger.debug(f"Convert and add bands... sat_data.id='{self.id}'")
        logger.debug(f"TIFF paths: {tiff_paths}")
        self.convert_and_add_bands(sat_data, tiff_paths, bands_strings)
        logger.debug(
            f"Successfully converting and adding bands done. sat_data.id='{self.id}'")

    def load_raster(self, file_path: str):
        logger.debug(f"Loading raster... file_path='{file_path}'")
        try:
            # Add media root to path if not already there
            if not MEDIA_ROOT in file_path:
                file_path = FileUtils.generate_path(MEDIA_ROOT, file_path)

            # Load raster using GDAL
            raster = GDALRaster(file_path, write=True)
            if raster is None:
                logger.error(
                    f"Failed to load raster because raster.srs.srid is 'None'. file_path='{file_path}'")
            else:
                logger.debug(
                    f"Sucessfully loaded raster. file_path='{file_path}'")
            return raster
        except Exception as e:
            logger.error(
                f"Could not load raster. file_path='{file_path}', error='{e}'")
            return None

    def set_manifest(self):
        """ Sets manifest attribute in SatData object."""
        # Set metadata
        logger.debug(f"Setting manifest path... sat_data.id='{self.id}'")
        manifest_path = self.path_dict["manifest"]
        self.sat_data.manifest = remove_media_root(manifest_path)
        logger.info(
            f"Set manifest. sat_data.id='{self.id}', sat_data.mission='{self.mission}', manifest_path='{manifest_path}'")

    def set_thumbnail(self):
        """ Sets thumbnail attribte in SatData object."""
        logger.debug(f"Setting thumbnail... sat_data.id='{self.id}'")

        # Get thumbnail path
        thumbnail_path = ""
        if self.sh_request:
            # Sentinel Hub Request
            # Check thumbnail file path
            # if .tar exists
            default_thumbnail_path = FileUtils.generate_path(
                self.extracted_abs_path, "default.png")
            # no .tar file
            response_thumbnail_path = FileUtils.generate_path(
                self.extracted_abs_path, "response.png")
            if os.path.exists(default_thumbnail_path):
                thumbnail_path = default_thumbnail_path
            elif os.path.exists(response_thumbnail_path):
                thumbnail_path = response_thumbnail_path
        else:
            # Archive upload
            thumbnail_path = self.path_dict["thumbnail"]

        # Set thumbnail
        if thumbnail_path:
            self.sat_data.thumbnail = remove_media_root(thumbnail_path)
            logger.info(
                f"Set thumbnail. sat_data.id='{self.id}', sat_data.mission='{self.mission}', thumbnail_path='{thumbnail_path}'")
        else:
            self.sat_data.thumbnail = ""
            logger.info(
                f"SatData object has no thumbnail image or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}', product_type='{self.sat_data.product_type}'")

    def set_eop_metadata(self):
        """ Sets eop metadata attribte in SatData object."""
        logger.debug(f"Setting eop metadata... sat_data.id='{self.id}'")
        eop_metadata_path = self.path_dict["eop_metadata"]

        if eop_metadata_path == "":
            logger.info(
                f"SatData object has no eop metadata xml or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")
        else:
            self.sat_data.eop_metadata = eop_metadata_path
            logger.info(
                f"Set eop metadata. sat_data.id='{self.id}', sat_data.mission='{self.mission}', eop_metadata_path='{eop_metadata_path}'")

    def set_xfdu_manifest(self):
        """ Sets xfdu manifest attribte in SatData object."""
        logger.debug(f"Setting xfdu manifest... sat_data.id='{self.id}'")
        xfdu_manifest_path = self.path_dict["xfdu_manifest"]

        if xfdu_manifest_path == "":
            logger.info(
                f"SatData object has no xfdu manifest xml or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")
        else:
            self.sat_data.xfdu_manifest = xfdu_manifest_path
            logger.info(
                f"Set xfdu manifest. sat_data.id='{self.id}', sat_data.mission='{self.mission}', xfdu_manifest_path='{xfdu_manifest_path}'")

    def set_manifest(self):
        """ Sets manifest attribute in SatData object."""
        logger.debug(f"Setting manifest... sat_data.id='{self.id}'")
        manifest_path = self.path_dict["manifest"]

        if manifest_path == "":
            logger.info(
                f"SatData object has no manifest xml or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")
        else:
            self.sat_data.manifest = manifest_path
            logger.info(
                f"Set manifest. sat_data.id='{self.id}', sat_data.mission='{self.mission}', manifest_path='{manifest_path}'")

    def set_inspire(self):
        """ Sets inspire attribte in SatData object."""
        logger.debug(f"Setting inspire... sat_data.id='{self.id}'")
        inspire_path = self.path_dict["inspire"]

        if inspire_path == "":
            logger.info(
                f"SatData object has no inspire xml or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")
        else:
            self.sat_data.inspire = inspire_path
            logger.info(
                f"Set inspire. sat_data.id='{self.id}', sat_data.mission='{self.mission}', inspire_path='{inspire_path}'")

    def set_mission(self):
        """ Sets mission attribute in SatData object."""
        self.sat_data.mission = self.mission
        logger.info(
            f"Set mission. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")

    def set_product_type(self):
        """ Sets product type attribute in SatData object."""
        logger.debug(f"Setting product type... sat_data.id='{self.id}'")
        sat_data = self.sat_data

        logger.debug(
            "Sentinel Hub Request" if self.sh_request else "Archive upload")
        if self.sh_request:
            # Sentinel Hub Request
            # Identify product type by `request.json`
            request_json_path = FileUtils.generate_path(
                sat_data.extracted_path, "request.json")
            if os.path.exists(request_json_path):
                request_json = json.loads(request_json_path)
                request_json_string = str(request_json)
                logger.error('Request JSON: ', request_json_string)

                product_type = request_json["request"]["payload"]["input"]["data"][0]["type"]
            else:
                # Unknown product type
                logger.info(
                    f"SatData object has no product type or mission/product type is not supported yet. sat_data.id='{sat_data.id}', sat_data.mission='{self.mission}'")
                # every product type has the "unknown" value, so does not matter which one to use
                product_type = S1AProdType.UNKNOWN.value  # use any unknown value
        else:
            # Archive upload
            # Identify product type by metadata
            logger.debug(
                f"Identifying '{self.mission}'s product type by metadata... sat_data.id='{sat_data.id}'")
            product_type = self.product_type_by_metadata()

            metadata_prod_types = S1AProdType.get_all() + S2AProdType.get_all() + \
                S2BProdType.get_all() + S3AProdType.get_all() + S3BProdType.get_all()
            if product_type in metadata_prod_types:
                logger.debug(
                    f"Identified '{self.mission}' SatData object. sat_data.id='{sat_data.id}'")
                # Sentinel-1A or Sentinel-3A
                logger.debug(
                    f"Extracted '{self.mission}' SatData object's product type '{product_type}'.")
            else:
                # Unknown product type
                logger.info(
                    f"Extracted product type '{product_type}' which is not supported yet. sat_data.id='{sat_data.id}', sat_data.mission='{self.mission}', product_type='{product_type}'")
                product_type = S1AProdType.UNKNOWN.value  # use any unknown value

        # Set product type in SatData object
        sat_data.product_type = product_type
        self.product_type = product_type
        logger.info(
            f"Set product type. sat_data.id='{sat_data.id}', product_type='{product_type}'")

    def product_type_by_metadata(self):
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
            metadata_path = FileUtils.generate_path(
                self.extracted_abs_path, "manifest.safe")
            logger.debug(
                f"Using keyword and metadata path for Sentinel-1A. keywords='{keywords}', metadata_path='{metadata_path}'")
        elif self.mission == SatMission.SENTINEL_3A.value or self.mission == SatMission.SENTINEL_3B.value:
            # Sentinel-3A with 'xfdumanifest.xml'
            keywords = ["sentinel3:productType"]
            # must set this path manually, as the "xfdu_manifest" attribute is set later
            metadata_path = FileUtils.generate_path(
                self.extracted_abs_path, "xfdumanifest.xml")
            logger.debug(
                f"Using keyword and metadata path for Sentinel-3A. keywords='{keywords}', metadata_path='{metadata_path}'")
        elif self.mission == SatMission.SENTINEL_2A.value or self.mission == SatMission.SENTINEL_2B.value:
            
            files = os.listdir(self.extracted_abs_path)
            logger.debug(
                f"Using keyword and metadata path for Sentinel-2A/B. files='{files}'")
            # Iterate over the files and check if the filename starts with the prefix
            # Metadata path could be "MTD_MSIL1C.xml" or "MTD_MSIL2A.xml
            metadata_path = ""
            keyword = []
            for file in files:
                if file.startswith("MTD"):
                    metadata_path = os.path.join(self.extracted_abs_path, remove_media_root(file))
                    keywords = ["PRODUCT_TYPE"]
                    logger.debug(
                        f"Metadata file found. metadata_path='{metadata_path}'")
                if metadata_path:
                    break

            # In case nothing was found, return "unknown"
            if metadata_path == "" or keywords == []:
                logger.error(
                    f"Could not find metadata file. extracted_abs_path='{self.extracted_abs_path}'")
                # every product type has the "unknown" value, so does not matter which one to use
                return S1AProdType.UNKNOWN.value
        else:
            logger.info(
                f"SatData object has no product type or mission/product type is not supported yet. sat_data.id='{self.id}', sat_data.mission='{self.mission}'")
            # every product type has the "unknown" value, so does not matter which one to use
            return S1AProdType.UNKNOWN.value

        logger.debug(
            f"Extracting product type from metadata... sat_data.id='{self.id}'")
        metadata_dict = FileUtils.xml_to_dict(metadata_path)

        # Search for product type value in metadata
        for keyword in keywords:
            product_type = FileUtils.get_dict_value_by_key(
                metadata_dict, keyword)
            if product_type:
                break

        logger.debug(f"Returned product type: '{product_type}'")
        if product_type:
            return product_type.lower()
        else:
            # every product type has the "unknown" value, so it does not matter which one to use
            return S1AProdType.UNKNOWN.value
