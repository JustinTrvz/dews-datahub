import os
from threading import Thread
from django.contrib.auth.models import User

from django.db import models
import uuid
import logging

from django.urls import reverse
from sat_data.enums.sat_mission import SatMission
from sat_data.enums.sat_prod_type import SatProdType

from utils.model_util import ModelUtil
from sat_data.enums.sat_band import SatBand
from dews.settings import IMAGES_FILES_PATH, MEDIA_ROOT, ARCHIVE_FILES_PATH, DB_USER
from utils.overwrite_storage import OverwriteStorage


def thumbnail_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    path = remove_media_root(instance.directory_path)
    return f"{path}/preview/{filename}"


def metadata_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    path = remove_media_root(instance.directory_path)
    return f"{path}/{filename}"


def archive_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
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
                               choices=SatMission.as_dict,
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
    metadata = models.FileField(max_length=255,
                                null=True,
                                blank=True,
                                upload_to=metadata_upload_path,
                                verbose_name="Metadata",
                                storage=OverwriteStorage())
    thumbnail = models.ImageField(max_length=255,
                                  null=True,
                                  blank=True,
                                  upload_to=thumbnail_upload_path,
                                  verbose_name="Thumbnail",
                                  storage=OverwriteStorage())
    creation_time = models.DateTimeField(auto_now_add=True)

    # Relationships
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, default=get_dews_user)

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
            from dews.sat_data.services.attr_adder import AttrAdder
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
        default=10, help_text="One pixel in meter")  # in meter
    aot_path = models.CharField(max_length=255, blank=True, null=True)
    scl_path = models.CharField(max_length=255, blank=True, null=True)
    tci_path = models.CharField(max_length=255, blank=True, null=True)
    wvp_path = models.CharField(max_length=255, blank=True, null=True)
    b01_path = models.CharField(max_length=255, blank=True, null=True)
    b02_path = models.CharField(max_length=255, blank=True, null=True)
    b03_path = models.CharField(max_length=255, blank=True, null=True)
    b04_path = models.CharField(max_length=255, blank=True, null=True)
    b05_path = models.CharField(max_length=255, blank=True, null=True)
    b06_path = models.CharField(max_length=255, blank=True, null=True)
    b07_path = models.CharField(max_length=255, blank=True, null=True)
    b08_path = models.CharField(max_length=255, blank=True, null=True)
    b8a_path = models.CharField(max_length=255, blank=True, null=True)
    b09_path = models.CharField(max_length=255, blank=True, null=True)
    b10_path = models.CharField(max_length=255, blank=True, null=True)
    b11_path = models.CharField(max_length=255, blank=True, null=True)
    b12_path = models.CharField(max_length=255, blank=True, null=True)

    # Relationships
    sat_data = models.OneToOneField(
        SatData, on_delete=models.CASCADE, related_name='band_info')

    # Meta data
    class Meta:
        db_table = "band_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id


class AreaInfo(models.Model):
    # Attributes
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    capture_time = models.DateTimeField(null=True)

    # Relationships
    sat_data = models.OneToOneField(
        SatData, on_delete=models.CASCADE, related_name='area_info')

    # Meta data
    class Meta:
        db_table = "area_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id


class ImageInfo(models.Model):
    # Attributes
    img_type = models.CharField(max_length=20)
    img_path = models.CharField(max_length=255)
    archived_img_paths = models.TextField()

    # Relationships
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

    # Meta data
    class Meta:
        db_table = "image_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id


class BoundLatitudes(models.Model):
    # Attributes
    north = models.FloatField()
    east = models.FloatField()
    south = models.FloatField()
    west = models.FloatField()

    # Relationships
    sat_data = models.OneToOneField(
        SatData, on_delete=models.CASCADE, related_name='bound_latitudes')

    # Meta data
    class Meta:
        db_table = "bound_latitudes"

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
        SatData, on_delete=models.CASCADE, related_name='capture_info')

    # Meta data
    class Meta:
        db_table = "capture_info"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id


class Calculation(models.Model):
    # Attributes
    status = models.CharField(max_length=50)

    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

    # Meta data
    class Meta:
        db_table = "calculation"

    # Methods
    def to_dict(self):
        return ModelUtil.to_dict(self)

    def __str__(self):
        return self.id
