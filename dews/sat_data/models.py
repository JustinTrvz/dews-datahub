from enum import Enum
import os
from threading import Thread
from django.contrib.auth.models import User

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


import uuid
import logging

from django.urls import reverse
from sat_data.enums.sat_mission import SatMission
from sat_data.enums.sat_prod_type import SatProdType
from sat_data.enums.status import Status


from utils.services.model_util import ModelUtil
from sat_data.enums.sat_band import SatBand
from dews.settings import IMAGES_FILES_PATH, MEDIA_ROOT, ARCHIVE_FILES_PATH, DB_USER
from utils.services.overwrite_storage import OverwriteStorage


def band_upload_path(instance, filename):
    path = remove_media_root(instance.sat_data.extracted_path)
    return f"{path}/{filename}"


def index_upload_path(instance, filename):
    path = remove_media_root(IMAGES_FILES_PATH)
    return f"{path}/{instance.sat_data.mission}/{instance.sat_data.id}/{filename}"


def thumbnail_upload_path(instance, filename):
    path = remove_media_root(instance.extracted_path)
    return f"{path}/preview/{filename}"


def metadata_upload_path(instance, filename):
    path = remove_media_root(instance.extracted_path)
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
    user, _ = User.objects.get_or_create(username=DB_USER)
    return user


class TimeTravel(models.Model):
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
    thumbnail = models.ImageField(max_length=255,
                                  null=True,
                                  blank=True,
                                  upload_to=f"time_travel/{mission}/{id}/thumbnail",
                                  verbose_name="Thumbnail",
                                  storage=OverwriteStorage())
    coordinates = models.PolygonField(blank=True,
                                      null=True,
                                      verbose_name="Polygon Coordinates")
    leaflet_coordinates = models.PolygonField(blank=True,
                                              null=True,
                                              verbose_name="Leaflet Coordinates")
    product_type = models.CharField(max_length=50,
                                    verbose_name="Product Type",
                                    default=SatProdType.UNKNOWN.value,
                                    blank=True)
    creation_time = models.DateTimeField(auto_now_add=True)


# Base class for satellite data
class SatData(models.Model):

    # Attributes
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False,
                          verbose_name="ID")
    name = models.CharField(max_length=255,
                            default="No name",
                            blank=True)
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
    band_tables = models.JSONField(max_length=2000,
                                   verbose_name="Band Tables",
                                   blank=True,
                                   null=True)
    processing_done = models.BooleanField(default=False,
                                          verbose_name="Processing Done",
                                          blank=True,
                                          null=True)
    archive = models.FileField(max_length=255,
                               null=True,
                               blank=True,
                               upload_to=archive_upload_path,
                               verbose_name="Archive",
                               storage=OverwriteStorage())
    mtd = models.FileField(max_length=255,
                           null=True,
                           blank=True,
                           upload_to=metadata_upload_path,
                           verbose_name="MTD",
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
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sat_datas',
        default=get_dews_user,
    )

    time_travel = models.ForeignKey(
        TimeTravel,
        on_delete=models.CASCADE,
        related_name='sat_datas',
        null=True,
        blank=True,
    )
    sh_request = models.ForeignKey(
        'SHRequest',
        on_delete=models.CASCADE,
        related_name='sat_datas',
        null=True,
        blank=True,
    )

    # Meta data
    class Meta:
        db_table = "sat_data"
        ordering = ["-creation_time"]  # descending order

    def get_absolute_url(self):
        return reverse("sat_data:sat_data_details_view", kwargs={"sat_data_id": self.id})

    # Methods
    def get_band(self, *required_bands):
        """
        Returns a Band object that contains all the required bands.

        Pass strings as separate arguments. For example: `get_band_info("aot", "b03", "b05")`

        See `Band` object for a list of all accessible bands.
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
        bands = self.band_set.all()

        for band in bands:
            # Check if all required bands have values in the BandInfo object
            if all(getattr(band, f"{band}_path") for band in required_bands):
                return band

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
        return f"SatData<'{self.id}'>"


class Band(models.Model):
    """ Represents a band image as raster. """
    # Attributes
    # id = models.IntegerField(primary_key=True, verbose_name="ID")
    range = models.IntegerField(
        default=0, help_text="One pixel in meter", blank=True)  # in meter
    type = models.CharField(max_length=50, blank=True, verbose_name="Type")
    raster = models.RasterField(null=True, blank=True, verbose_name="Raster")
    srid = models.IntegerField(default=4326, blank=True, verbose_name="SRID")
    band_file = models.FileField(
        max_length=255, blank=True, verbose_name="Band file", upload_to=band_upload_path)

    # Relationships
    sat_data = models.ForeignKey(
        SatData, on_delete=models.CASCADE, related_name="bands")

    # Meta data
    class Meta:
        db_table = "band"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return f"Band<SatData '{self.sat_data.id}'>"


class Area(models.Model):
    # Attributes
    country = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(blank=True, null=True)
    stop_time = models.DateTimeField(blank=True, null=True)

    # Relationships
    sat_data = models.OneToOneField(
        SatData,
        on_delete=models.CASCADE,
        related_name='area',
        primary_key=True,
    )  # Primary key!

    # Meta data
    class Meta:
        db_table = "area"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return f"Area<SatData '{self.sat_data.id}'>"


class Index(models.Model):
    # Attributes
    # id = models.IntegerField(primary_key=True, verbose_name="ID")
    idx_type = models.CharField(max_length=20)
    img = models.ImageField(max_length=255,
                            null=True,
                            blank=True,
                            upload_to=index_upload_path,
                            verbose_name="Index img",
                            storage=OverwriteStorage())
    archived_img_paths = models.TextField()

    # Relationships
    sat_data = models.ForeignKey(
        SatData, on_delete=models.CASCADE, related_name="index")

    # Meta data
    class Meta:
        db_table = "index"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return f"Index<'{self.id}', SatData '{self.sat_data.id}'>"

class SHRequest(models.Model):
    """ Represents a request to the Sentinel Hub API."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID",
    )
    mission = models.CharField(
        max_length=50,
        blank=False,
        null=False,
    )
    bands = ArrayField(
        models.CharField(max_length=300),
        default=list,
    )
    resolution = models.IntegerField(blank=False, null=False)
    # can be empty, no need to force index calculation
    metrics_to_calc = ArrayField(
        models.CharField(max_length=300), default=list)
    creation_time = models.DateTimeField(
        auto_now_add=True,  # when the request was created
    )
    start_date = models.DateField(
        blank=False,
        null=False,
    )
    # could be the same as `start_date`
    end_date = models.DateField(
        blank=False,
        null=False,
    )
    coordinates = models.PolygonField(
        blank=True,
        null=True,
        verbose_name="Polygon Coordinates",
    )
    progress = models.CharField(
        max_length=20,
        blank=True,
        default=Status.IN_PROGRESS.value,
    )

    # Relationships
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        default=get_dews_user,
    )

    # Meta data
    class Meta:
        db_table = "sh_request"
        ordering = ["-creation_time"]  # descending order

    def __str__(self):
        return f"SHRequest<'{self.id}'>"
        # return f"SHRequest<SatData '{self.sat_data.id}'>"
