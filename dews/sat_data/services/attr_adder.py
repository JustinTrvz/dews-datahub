from datetime import datetime
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
    metadata_dict = {}
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

    def __init__(self, sat_data: SatData, extracted_path: str, mission: str) -> None:
        logger.debug("AttrAdder object created.")
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
        self.set_mtd()
        self.set_manifest()
        self.set_xfdu_manifest()
        self.set_inspire()
        self.set_eop_metadata()
        self.set_thumbnail()
        logger.debug(
            f"Set manifest, xfdu manifest, inspire, eop metadata, thumbnail and img paths. sat_data.id='{self.id}'")

        # Set other info
        self.set_coordinates()
        self.set_area_details()
        self.set_time_series()

        logger.debug(
            f"Set coordinates, capture info and time series. sat_data.id='{self.id}'")
        
        # Long time consuming process:
        self.set_bands()

        # Save operation is executed in views
        logger.debug(f"AttrAdder done! sat_data.id='{self.id}'")
        return

    def set_mtd(self):
        """ Sets mtd attribte in SatData object."""
        logger.debug(f"Setting mtd ... sat_data.id='{self.id}'")
        mtd_path = self.path_dict["mtd"]

        if mtd_path == "":
            logger.info(
                f"SatData object has no 'MTD_*.xml' or mission/product type is not supported yet. id='{self.sat_data.id}', mission='{self.mission}'")
        else:
            self.sat_data.mtd = mtd_path
            logger.info(
                f"Set mtd. id='{self.sat_data.id}', mission='{self.mission}', mtd_path='{mtd_path}'")

    def set_name(self):
        logger.debug(f"Setting name... sat_data.id='{self.id}'")
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
        area_info = Area(sat_data=self.sat_data,
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

        if self.product_type in PathFinder.has_manifest_prod_types:
            # Get coordinates from 'manifest.safe' file
            logger.debug(
                f"Identified '{self.mission}' SatData object. id='{sat_data.id}'")
            self.metadata_dict = FileUtils.xml_to_dict(sat_data.manifest.url)
            coordinates = FileUtils.get_dict_value_by_key(
                self.metadata_dict, "gml:coordinates").lower()

            coordinates_splitted = coordinates.split()
            if "," in coordinates:
                # Comma seperated coordinates
                coordinate_tuples = [tuple(map(float, pair.split(',')))
                                     for pair in coordinates_splitted]
            else:
                # Space seperated coordinates
                coordinate_tuples = [(float(coordinates_splitted[i]), float(coordinates_splitted[i + 1]))
                                     for i in range(0, len(coordinates_splitted), 2)]

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

    def set_bands(self):
        """ Sets bands in SatData object."""
        logger.debug(f"Setting bands... sat_data.id='{self.id}'")
        sat_data = self.sat_data

        if sat_data.product_type in self.tiff_file_prod_types:
            # TIFF files
            logger.debug(
                f"Product type '{sat_data.product_type}' has tiff file bands.")
            self.__set_tiff_bands(sat_data)
        elif sat_data.product_type in self.jp2_file_prod_types:
            # JP2 files
            logger.debug(
                f"Product type '{sat_data.product_type}' has jp2 file bands.")
            self.__set_jp2_bands(sat_data)
        
        # Check if extracted path contains .nc files
        if self.contains_file_by_ext(self.extracted_path, ".nc"):
            logger.debug(
                f"Product type '{sat_data.product_type}' has nc file bands.")
            self.__set_nc_bands(sat_data)
        else:
            # No bands available
            logger.info(
                f"Did not add bands because product type '{sat_data.product_type}' has no band support yet.")
            return

        logger.debug(
            f"Set bands to SatData object... sat_data.id='{self.id}'")

    def contains_file_by_ext(self, directory, ext):
        # Check if the directory contains any .nc files
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
            f"Listing all possible bands in 'extracted_path' directory. id='{self.id}'")
        
        # Get all .nc file paths
        nc_paths = self.get_file_paths_by_ext(self.extracted_path, ".nc")

        # Convert band to raster and import to database
        logger.debug(f"Convert and add bands... sat_data.id='{self.id}'")
        self.convert_and_add_bands(sat_data, nc_paths, [".nc"])
        logger.debug(
            f"Successfully converting and adding bands done. sat_data.id='{self.id}'")


    def __set_jp2_bands(self, sat_data: SatData):
        # List all possible bands in "IMG_DATA" path
        logger.debug(
            f"Listing all possible bands in 'IMG_DATA' directory. id='{self.id}'")

        # Get all .jp2 file paths
        mtd_dict = FileUtils.xml_to_dict(
            FileUtils.generate_path(MEDIA_ROOT, self.path_dict["mtd"]))
        jp2_paths = FileUtils.get_all_dict_values_by_key(
            mtd_dict, "IMAGE_FILE")
        logger.debug(f"jp2_paths: {jp2_paths}")
        logger.debug(f"extracted_path: {self.extracted_path}")
        # add extracted path and extension
        jp2_paths = [FileUtils.generate_path(
            self.extracted_path, file_path) + ".jp2" for file_path in jp2_paths]

        # Band sub strings (B01, B02, ..., B8A, B09, ...)
        bands_substrings = [f"B{str(i).zfill(2)}" if i != 8 else "B8A" for i in range(
            1, 13)] + ["AOT", "TCI", "WVP", "SCL"]
        sat_data.save()

        # Convert band to raster and import to database
        logger.debug(f"Convert and add bands... sat_data.id='{self.id}'")
        self.convert_and_add_bands(sat_data, jp2_paths, bands_substrings)
        logger.debug(
            f"Successfully converting and adding bands done. sat_data.id='{self.id}'")

    def convert_and_add_bands(self, sat_data: SatData, band_paths, bands_substrings):
        sat_data.band_tables = {
            "unknown": [],
            "r10m": [],
            "r20m": [],
            "r60m": [],
        }
        sat_data.save()
        for band_path in band_paths:
            for substring in bands_substrings:
                if substring in band_path:
                    logger.info(
                        f"File '{band_path}' contains the substring '{substring}'.")

                    # Split band path to search for range part
                    band_path_splitted = band_path.split("/")
                    range_string = "unknown"

                    # Search for "R10m", "R20m", etc.
                    if len(band_path_splitted) > 2:
                        range_part = band_path_splitted[-2]
                        match = re.search(r"R\d+m", range_part)
                        if match:
                            range_string = match.group(0).lower()
                            substring = f"{substring}_{range_string}"
                            logger.debug(
                                f"Added range part to substring. substring='{substring}'")
                    
                    # Get file name if .nc file
                    if substring == ".nc":
                        substring = band_path_splitted[-1]
                            
                    # Shorten mission name
                    mission = sat_data.mission
                    if "-" in mission:
                        mission_split = mission.split("-")
                        mission = f"{mission_split[0][0]}{mission_split[1]}"

                    # Create table name
                    table_name = f"{sat_data.id}_{substring}".lower()
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
                            f"Failed to import raster '{substring}'. error='{e}', band_path='{band_path}'")
                        continue
                    logger.info(
                        f"Successfully imported raster '{substring}'. band_path='{band_path}'")

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

    # def create_band(self, sat_data, raster, type, band_path):
    #     logger.debug(
    #         f"Creating Band object. attr_name='{type}', sat_data='{sat_data}'")
    #     # Create band object
    #     band = Band(range=10,  # TODO: get range from metadata
    #                 type=type,
    #                 band_path=band_path,
    #                 sat_data=sat_data,
    #                 )

    #     # Set band_file attribute
    #     band.band_file = remove_media_root(band_path)
    #     # Set raster attribute if available
    #     if raster:
    #         band.raster = raster
    #     logger.debug(
    #         f"Created Band object. attr_name='{type}', sat_data='{sat_data}'")

    #     # Save band object
    #     try:
    #         band.save()
    #         logger.debug(f"Saved Band object. band='{band}'")
    #     except Exception as e:
    #         logger.error(
    #             f"Could not save Band object. err='{e}', band='{band}', type='{type}', raster='{raster}', sat_data='{sat_data}'")
    #         return

    def __set_tiff_bands(self, sat_data):
        # List all possible bands in "measurement path"
        logger.debug(
            f"Listing all possible bands in 'measurement' directory. id='{self.id}'")
        tiff_paths = os.listdir(f"{self.extracted_path}/measurement")

        # Generate a list of band substrings
        # ["b-001", "b-002", ...]
        logger.debug("Generate a list of band substrings.")
        bands_substrings = [
            f"b-{str(i).zfill(3)}" for i in range(1, 13)] + ["b-08a", "aot", "scl", "tci", "wvp"]
        logger.debug(f"Band substrings: {bands_substrings}")

        # Convert band to raster and import to database
        logger.debug(f"Convert and add bands... sat_data.id='{self.id}'")
        self.convert_and_add_bands(sat_data, tiff_paths, bands_substrings)
        logger.debug(
            f"Successfully converting and adding bands done. sat_data.id='{self.id}'")

        # # Iterate through the bands and check for substrings
        # logger.debug(
        #     f"Iterate through the image files and check for 'b???' substring. id='{self.id}'")
        # sat_data.save()
        # for tiff_path in tiff_paths:
        #     for band_substring in bands_substrings:
        #         if band_substring in tiff_path:
        #             logger.info(
        #                 f"File '{tiff_path}' contains the substring '{band_substring}'.")
        #             # Update the model attribute with the full path
        #             attr_name = f"b{band_substring[3:]}"
        #             band_path = f"{sat_data.extracted_path}/measurement/{tiff_path}"

        #             raster = self.load_raster(band_path)
        #             logger.debug(f"Loaded raster. band_path='{band_path}'")

        #             self.create_band(
        #                 sat_data,
        #                 raster,
        #                 attr_name,
        #                 band_path,
        #             )

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

        # # Method 1: Identify product type by file name

        # if self.mission == SatMission.SENTINEL_2B.value:
        #     logger.debug(
        #         f"Identifying {self.mission}'s product type by file name... id='{sat_data.id}'")
        #     # Sentinel-2B
        #     product_type = self.product_type_by_filename(sat_data)
        #     if product_type in S2BProdType.get_all():
        #         logger.debug(
        #             f"Extracted '{self.mission}' SatData object's product type '{product_type}'.")
        #         sat_data.product_type = product_type
        #         self.product_type = product_type
        #         logger.info(
        #             f"Set product type. id='{sat_data.id}', product_type='{product_type}'")
        #     else:
        #         logger.info(
        #             f"SatData object has no product type or mission/product type is not supported yet. id='{sat_data.id}', mission='{self.mission}', product_type='{product_type}'")
        #     return

        # Method 2: Identify product type by metadata
        logger.debug(
            f"Identifying '{self.mission}'s product type by metadata... id='{sat_data.id}'")
        product_type = self.product_type_by_metadata(
            self.extracted_path, sat_data)
        logger.debug(S1AProdType.get_all() +
                     S3AProdType.get_all() + S3BProdType.get_all())
        metadata_prod_types = S1AProdType.get_all() + S2AProdType.get_all() + \
            S2BProdType.get_all() + S3AProdType.get_all() + S3BProdType.get_all()
        if product_type in metadata_prod_types:
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
        # # Sentinel-2B
        # logger.debug(
        #     f"Identified '{self.mission}' SatData object. id='{sat_data.id}'")

        # # List all files in the extracted path
        # files = os.listdir(self.extracted_path)
        # # Check if any of the files start with "MTD"
        # product_type = S2BProdType.UNKNOWN.value
        # for file in files:
        #     if file.startswith('MTD'):
        #         # the file has the name MTD_*.xml now extract the * part
        #         product_type = file.split('_')[1].split('.')[0].lower()
        #         break
        # # returns "unknown" if no metadata was found
        # logger.debug(f"Returned product type: '{product_type}'")
        # return product_type.lower()
        # TODO: remove method or rewrite -> S2A and S2B use meta data now
        return S2AProdType.UNKNOWN.value

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
        elif self.mission == SatMission.SENTINEL_2A.value or self.mission == SatMission.SENTINEL_2B.value:
            files = os.listdir(extracted_path)
            logger.debug(
                f"Using keyword and metadata path for Sentinel-2A/B. files='{files}'")
            # Iterate over the files and check if the filename starts with the prefix
            # Metadata path could be "MTD_MSIL1C.xml" or "MTD_MSIL2A.xml
            metadata_path = ""
            keyword = []
            for file in files:
                if file.startswith("MTD"):
                    metadata_path = os.path.join(extracted_path, file)
                    keywords = ["PRODUCT_TYPE"]
                    logger.debug(
                        f"Metadata file found. metadata_path='{metadata_path}'")
                if metadata_path:
                    break

            # In case nothing was found, return "unknown"
            if metadata_path == "" or keywords == []:
                logger.error(
                    f"Could not find metadata file. extracted_path='{extracted_path}'")
                # every product type has the "unknown" value, so does not matter which one to use
                return S1AProdType.UNKNOWN.value
        else:
            logger.info(
                f"SatData object has no product type or mission/product type is not supported yet. id='{sat_data.id}', mission='{self.mission}'")
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
            # every product type has the "unknown" value, so does not matter which one to use
            return S1AProdType.UNKNOWN.value
