import os
from threading import Thread
from django.contrib.auth.models import User

from django.contrib.gis.db import models
import uuid
import logging

from django.urls import reverse
from sat_data.enums.sat_mission import SatMission
from sat_data.enums.sat_prod_type import SatProdType

from utils.services.model_util import ModelUtil
from sat_data.enums.sat_band import SatBand
from dews.settings import IMAGES_FILES_PATH, MEDIA_ROOT, ARCHIVE_FILES_PATH, DB_USER
from utils.services.overwrite_storage import OverwriteStorage


def band_upload_path(instance, filename):
    path = remove_media_root(instance.directory_path)
    return f"{path}/measurement/{filename}"


def index_upload_path(instance, filename):
    path = remove_media_root(IMAGES_FILES_PATH)
    return f"{path}/{instance.sat_data.mission}/{instance.sat_data.id}/{filename}"


def thumbnail_upload_path(instance, filename):
    path = remove_media_root(instance.directory_path)
    return f"{path}/preview/{filename}"


def metadata_upload_path(instance, filename):
    path = remove_media_root(instance.directory_path)
    return f"{path}/{filename}"


def archive_upload_path(instance, filename):
    path = remove_media_root(ARCHIVE_FILES_PATH)
    return f"{path}/{filename}"


def remove_media_root(path):
    path = str(path)
    if path.startswith(MEDIA_ROOT):
        return path[len(MEDIA_ROOT) + 1:]
    return path


def get_dews_user():
    return User.objects.get_or_create(username=DB_USER)

# Base class for satellite data



class SatData(models.Model):

    # Attributes
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          verbose_name="ID")
    name = models.CharField(max_length=100,
                            default="No name",
                            verbose_name="Name")
    mission = models.CharField(max_length=50,
                               verbose_name="Mission",
                               default=SatMission.UNKNOWN.value,
                               blank=True)
    product_type = models.CharField(max_length=50,
                                    verbose_name="Product Type",
                                    default=SatProdType.UNKNOWN.value,
                                    blank=True)
    extracted_path = models.CharField(max_length=255,
                                      verbose_name="Extracted Path",
                                      blank=True)
    archive = models.FileField(max_length=255,
                               null=False,
                               blank=False,
                               upload_to=archive_upload_path,
                               verbose_name="Archive",
                               storage=OverwriteStorage())
    manifest = models.FileField(max_length=255,
                                null=True,
                                blank=True,
                                upload_to=metadata_upload_path,
                                verbose_name="Manifest",
                                storage=OverwriteStorage())
    eop_metadata = models.FileField(max_length=255,
                                null=True,
                                blank=True,
                                upload_to=metadata_upload_path,
                                verbose_name="EOP Metadata",
                                storage=OverwriteStorage())
    xfdu_manifest = models.FileField(max_length=255,
                                null=True,
                                blank=True,
                                upload_to=metadata_upload_path,
                                verbose_name="Xfdu Manifest",
                                storage=OverwriteStorage())
    inspire = models.FileField(max_length=255,
                                null=True,
                                blank=True,
                                upload_to=metadata_upload_path,
                                verbose_name="Inspire",
                                storage=OverwriteStorage())
    thumbnail = models.ImageField(max_length=255,
                                  null=True,
                                  blank=True,
                                  upload_to=thumbnail_upload_path,
                                  verbose_name="Thumbnail",
                                  storage=OverwriteStorage())
    creation_time = models.DateTimeField(auto_now_add=True)
    coordinates = models.PolygonField(blank=True,
                                      null=True,
                                      verbose_name="Polygon Coordinates")
    leaflet_coordinates = models.PolygonField(blank=True,
                                      null=True,
                                      verbose_name="Leaflet Coordinates")

    # Relationships
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, default=get_dews_user)
    
    # time_series = models.ForeignKey(TimeSeries, related_name='sat_data', on_delete=models.CASCADE)

    # Meta data
    class Meta:
        db_table = "sat_data"
        ordering = ["-creation_time"]  # descending order

    def get_absolute_url(self):
        return reverse("sat_data:details_view", kwargs={"sat_data_id": self.id})

    # Methods
    @staticmethod
    def create(source_path: str, mission: str, extracted_path: str):
        # Check sat mission
        if not mission.lower() in [sat_mission.value.lower() for sat_mission in SatMission]:
            logging.error(
                f"Mission '{mission}' is not a valid satellite mission! Please use e.g. 'sentinel-1a' or 'sentinel-2b'.")
            return None

        try:
            dews_user = User.objects.get(username="dews")

            # Create satellite data object
            sat_data = SatData(
                mission=mission.lower(),
                directory_path=extracted_path,
                user=dews_user,
            )
            # Set archive path
            sat_data.archive = remove_media_root(source_path)

            logging.info(
                "Created SatData object (not saved to database yet).")

            # Add mission and instrument specific attributes
            if mission == SatMission.SENTINEL_1A.value:
                # Sentinel-1A
                # Metadata
                metadata_path = os.path.join(
                    remove_media_root(extracted_path), "manifest.safe")
                sat_data.metadata = metadata_path
                # .../manifest.safe
                logging.info(
                    f"Added metadata path. metadata_path='{metadata_path}'")
                # Thumbnail
                thumbnail_path = os.path.join(remove_media_root(
                    extracted_path), "preview", "thumbnail.png")
                sat_data.thumbnail = thumbnail_path  # .../preview/thumbnail.png
                logging.info(
                    f"Added thumbnail path. thumbnail_path='{thumbnail_path}'")

            # Save satellite data object
            sat_data.save()
            id = sat_data.id
            logging.info(f"Saved SatData object to database. id='{id}'")

            # Calculations in background
            from sat_data.services.attr_adder import AttrAdder
            attr_adder = AttrAdder(sat_data)
            calc_thread = Thread(target=lambda: attr_adder.start())
            calc_thread.start()
            logging.info(f"Calculation attributes in background... id='{id}'")

            logging.info(
                f"Successfully created a SatData object. id='{id}', directory_path='{extracted_path}', user_id='{DB_USER}', mission='{mission}'")

            return sat_data
        except Exception as e:
            logging.error(
                f"Failed to create SatData object. error='{e}', source_path='{source_path}', mission='{mission}'")
            return None

    def get_band_info(self, *required_bands):
        """
        Returns a BandInfo object that contains all the required bands.

        Pass strings as separate arguments. For example: `get_band_info("aot", "b03", "b05")`

        See `BandInfo` object for a list of all accessible bands.
        """
        # Check if bands allowed
        allowed_bands = SatBand.get_all()

        required_bands = [band.lower() for band in required_bands]
        for band in required_bands:
            if band not in allowed_bands:
                logging.error(
                    f"Band '{band}' is not allowed or does not exist! allowed_bands='{allowed_bands}, required_bands='{required_bands}''")
                return None

        # Reverse relation accessible through "<related_model>_set"
        band_infos = self.bandinfo_set.all()

        for band_info in band_infos:
            # Check if all required bands have values in the BandInfo object
            if all(getattr(band_info, f"{band}_path") for band in required_bands):
                return band_info

        logging.warning(
            f"Could not find a band info item containing all required bands. required_bands='{required_bands}''")
        return None

    def img_save_loc(self, index_name: str = ""):
        """
        Returns location where the images for the current satellite data object should be stored.

        Pass an index name like "ndvi" or "evi" if you want to get the specific image save location.
        """
        return IMAGES_FILES_PATH / self.mission / self.id / index_name

    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return str(self.id)
    
class BandInfo(models.Model):
    # Attributes
    range = models.IntegerField(
        choices=[(10, '10'), (20, '20'), (60, '60')],
        default=10, help_text="One pixel in meter", blank=True)  # in meter
    aot = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="AOT",
                            storage=OverwriteStorage(),
                            default="None")
    scl = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="SCL",
                            storage=OverwriteStorage(),
                            default="None")
    tci = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="TCI",
                            storage=OverwriteStorage(),
                            default="None")
    wvp = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="WVP",
                            storage=OverwriteStorage(),
                            default="None")
    b01 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B01",
                            storage=OverwriteStorage(),
                            default="None")
    b02 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B02",
                            storage=OverwriteStorage(),
                            default="None")
    b03 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B03",
                            storage=OverwriteStorage(),
                            default="None")
    b04 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B04",
                            storage=OverwriteStorage(),
                            default="None")
    b05 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B05",
                            storage=OverwriteStorage(),
                            default="None")
    b06 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B06",
                            storage=OverwriteStorage(),
                            default="None")
    b07 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B0",
                            storage=OverwriteStorage(),
                            default="None")
    b08 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B07",
                            storage=OverwriteStorage(),
                            default="None")
    b8a = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B8A",
                            storage=OverwriteStorage(),
                            default="None")
    b09 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B09",
                            storage=OverwriteStorage(),
                            default="None")
    b10 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B10",
                            storage=OverwriteStorage(),
                            default="None")
    b11 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B11",
                            storage=OverwriteStorage(),
                            default="None")
    b12 = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=band_upload_path,
                            verbose_name="B12",
                            storage=OverwriteStorage(),
                            default="None")

    # Relationships
    sat_data = models.OneToOneField(
        SatData, on_delete=models.CASCADE, related_name='band_info', primary_key=True)  # Primary key!

    # Meta data
    class Meta:
        db_table = "band_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return f"BandInfo<SatData '{self.sat_data.id}'>"


class AreaInfo(models.Model):
    # Attributes
    country = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)

    # Relationships
    sat_data = models.OneToOneField(
        SatData, on_delete=models.CASCADE, related_name='area_info', primary_key=True)  # Primary key!

    # Meta data
    class Meta:
        db_table = "area_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id


class IndexInfo(models.Model):
    # Attributes
    idx_type = models.CharField(max_length=20)
    img = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=index_upload_path,
                            verbose_name="Index img",
                            storage=OverwriteStorage())
    archived_img_paths = models.TextField()

    # Relationships
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

    # Meta data
    class Meta:
        db_table = "index_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id



class CaptureInfo(models.Model):
    # Attributes
    product_start_time = models.DateTimeField()
    product_stop_time = models.DateTimeField()
    product_type = models.CharField(max_length=50)

    # Relationships
    sat_data = models.OneToOneField(
        SatData, on_delete=models.CASCADE, related_name='capture_info', primary_key=True)  # Primary key!

    # Meta data
    class Meta:
        db_table = "capture_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id
