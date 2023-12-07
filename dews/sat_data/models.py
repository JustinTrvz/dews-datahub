from django.contrib.auth.models import User

from django.db import models
from datetime import datetime
import uuid
import logging
from sat_data.enums.satellite_mission import SatelliteMission

from utils.model_util import ModelUtil
from sat_data.enums.bands import SatelliteBand
from dews.settings import EXTRACTED_FILES_PATH, IMAGES_FILES_PATH

def thumbnail_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "{0}/preview/{1}".format(instance.directory_path, filename)
    return "/dews/media/sat_data/images/{0}/{1}/thumbnail/{2}".format(instance.mission, instance.id, filename)

def metadata_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "{0}/{1}".format(instance.directory_path, filename)
    return "/dews/media/sat_data/images/{0}/{1}/metadata/{2}".format(instance.mission, instance.id, filename)

# Base class for satellite data
class SatData(models.Model):
    
    # Attributes
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mission = models.CharField(max_length=50, choices=SatelliteMission.as_tuple)
    product_type = models.CharField(max_length=50)
    directory_path = models.CharField(max_length=255)
    metadata= models.FileField(null=True, blank=True, upload_to=metadata_upload_path)
    # metadata_path = models.CharField(max_length=255)
    thumbnail = models.ImageField(null=True, blank=True, upload_to=thumbnail_upload_path)
    # thumbnail_path = models.CharField(max_length=255)

    # Foreign keys
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)

    # Meta data
    class Meta:
        db_table = "sat_data"

    # Methods
    def band_info(self, *required_bands):
        """
        Returns a BandInfo object that contains all the required bands.

        Pass strings as separate arguments. For example: `get_band_info("aot", "b03", "b05")`

        See `BandInfo` object for a list of all accessible bands.
        """
        # Check if bands allowed
        allowed_bands = SatelliteBand.get_all()

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
        return self.id


class BandInfo():
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

    # Foreign keys
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

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
    area_name = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    creation_time = models.DateTimeField(auto_now_add=True)
    capture_time = models.DateTimeField(null=True)

    # Foreign keys
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

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

    # Foreign keys
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

    # Foreign keys
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

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

    # Foreign keys
    sat_data = models.ForeignKey(SatData, on_delete=models.CASCADE)

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
    result = models.CharField(max_length=50)

    # Foreign keys
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
