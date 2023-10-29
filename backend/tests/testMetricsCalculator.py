import unittest
import uuid

from os.path import exists

from backend.statistics.metrics_calculator import MetricsCalculator
from backend.config import *

class TestMetricsCalculator(unittest.TestCase):
    # Satellite image paths
    img_data_path = EXTRACTED_FILES_PATH + "/sentinel-2b/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.SAFE/GRANULE/L2A_T32UPE_A032595_20230603T103434/IMG_DATA"
    # Range 10m
    r10m_path = img_data_path + "/R10m"
    band_02_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B02_10m.jp2"  # BLUE
    band_03_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B03_10m.jp2"  # GREEN
    band_04_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B04_10m.jp2"  # RED
    band_08_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B08_10m.jp2"  # VNIR
    # Range 20m
    r20m_path = img_data_path + "/R20m"
    band_02_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B02_20m.jp2"  # BLUE
    band_03_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B03_20m.jp2"  # GREEN
    band_04_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B04_20m.jp2"  # RED
    band_8a_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B8A_20m.jp2"  # VNIR
    band_11_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B11_20m.jp2"  # SWIR
    band_12_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B12_20m.jp2"  # SWIR
    # Range 60m
    r60m_path = img_data_path + "/R60m"
    band_02_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B02_60m.jp2"  # BLUE
    band_03_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B03_60m.jp2"  # GREEN
    band_04_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B04_60m.jp2"  # RED
    band_8a_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B8A_60m.jp2"  # VNIR
    band_12_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B12_60m.jp2"  # SWIR
    test_files_location = "backend/tmp/files/images"
    sid_id = uuid.uuid4()  # random ID

    # NDVI
    def test_calculate_ndvi(self):
        save_location = MetricsCalculator.calculate_ndvi(
            sid_id=self.sid_id,
            image_path_04=self.band_04_r10m_path,
            image_path_08=self.band_08_r10m_path,
            save_location=self.test_files_location,
        )
        self.assertTrue(exists(save_location))

    # EVI
    def test_calculate_evi(self):
        save_location = MetricsCalculator.calculate_evi(
            sid_id=self.sid_id,
            image_path_02=self.band_02_r20m_path,
            image_path_04=self.band_04_r20m_path,
            image_path_8a=self.band_8a_r20m_path,
            save_location=self.test_files_location,
        )
        self.assertTrue(exists(save_location))

    # NDWI
    def test_calculate_ndwi(self):
        save_location = MetricsCalculator.calculate_ndwi(
            sid_id=self.sid_id,
            image_path_03=self.band_03_r10m_path,
            image_path_08=self.band_08_r10m_path,
            save_location=self.test_files_location,
        )
        self.assertTrue(exists(save_location))

    # Moisture index
    def test_calculate_moisture(self):
        save_location = MetricsCalculator.calculate_moisture(
            sid_id=self.sid_id,
            image_path_8a=self.band_8a_r20m_path,
            image_path_11=self.band_12_r20m_path,
            save_location=self.test_files_location,
        )
        self.assertTrue(exists(save_location))

    # NSDI
    def test_calculate_nsdi(self):
        save_location = MetricsCalculator.calculate_ndsi(
            sid_id=self.sid_id,
            image_path_03=self.band_03_r20m_path,
            image_path_11=self.band_11_r20m_path,
            save_location=self.test_files_location,
        )
        self.assertTrue(exists(save_location))

    # RGB
    def test_create_rgb_img(self):
        save_location = MetricsCalculator.create_rgb_img(
            sid_id=self.sid_id,
            blue_band_02=self.band_02_r20m_path,
            green_band_03=self.band_03_r20m_path,
            red_band_04=self.band_04_r20m_path,
            save_location=self.test_files_location,
        )
        self.assertTrue(exists(save_location))
