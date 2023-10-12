import unittest
import uuid

from os.path import exists
from backend.models.satellite_image_data import SatelliteImageData

from backend.utils.metrics_calculator import MetricsCalculator


class TestMetricsCalculator(unittest.TestCase):
    # Satellite image paths
    # TODO: replace absolute paths
    # Range 10m
    r10m_path = "/home/jtrvz/Git/remote_sensing_analysis/moisture_detector/test_files/extracted/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.SAFE/GRANULE/L2A_T32UPE_A032595_20230603T103434/IMG_DATA/R10m"
    band_02_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B02_10m.jp2"  # BLUE
    band_03_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B03_10m.jp2"  # GREEN
    band_04_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B04_10m.jp2"  # RED
    band_08_r10m_path = f"{r10m_path}/T32UPE_20230603T102559_B08_10m.jp2"  # VNIR
    # Range 20m
    r20m_path = "/home/jtrvz/Git/remote_sensing_analysis/moisture_detector/test_files/extracted/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.SAFE/GRANULE/L2A_T32UPE_A032595_20230603T103434/IMG_DATA/R20m"
    band_02_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B02_20m.jp2"  # BLUE
    band_03_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B03_20m.jp2"  # GREEN
    band_04_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B04_20m.jp2"  # RED
    band_8a_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B8A_20m.jp2"  # NIR
    band_12_r20m_path = f"{r20m_path}/T32UPE_20230603T102559_B12_20m.jp2"  # TODO: ?
    # Range 60m
    r60m_path = "/home/jtrvz/Git/remote_sensing_analysis/moisture_detector/test_files/extracted/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.SAFE/GRANULE/L2A_T32UPE_A032595_20230603T103434/IMG_DATA/R60m"
    band_02_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B02_60m.jp2"  # BLUE
    band_03_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B03_60m.jp2"  # GREEN
    band_04_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B04_60m.jp2"  # RED
    band_8a_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B8A_60m.jp2"  # NIR
    band_12_r60m_path = f"{r60m_path}/T32UPE_20230603T102559_B12_60m.jp2"  # TODO: ?
    test_files_location = "/home/jtrvz/Git/remote_sensing_analysis/moisture_detector/test_files"
    sid_id = uuid.uuid4()  # random ID

    def test_calculate_ndvi(self):
        save_location = MetricsCalculator.calculate_ndvi(
            sid_id=self.sid_id,
            image_path_04=self.band_04_r20m_path,
            image_path_8a=self.band_8a_r20m_path,
            save_location=f"{self.test_files_location}/indexes",
        )
        self.assertTrue(exists(save_location))

    def test_calculate_evi(self):
        save_location = MetricsCalculator.calculate_evi(
            sid_id=self.sid_id,
            image_path_02=self.band_02_r20m_path,
            image_path_04=self.band_04_r20m_path,
            image_path_8a=self.band_8a_r20m_path,
            save_location=f"{self.test_files_location}/indexes",
        )
        self.assertTrue(exists(save_location))

    def test_calculate_ndwi(self):
        save_location = MetricsCalculator.calculate_ndwi(
            sid_id=self.sid_id,
            image_path_03=self.band_03_r10m_path,
            image_path_08=self.band_08_r10m_path,
            save_location=f"{self.test_files_location}/indexes",
        )
        self.assertTrue(exists(save_location))

    def test_calculate_water_content(self):
        save_location = MetricsCalculator.calculate_water_content(
            sid_id=self.sid_id,
            image_path_8a=self.band_8a_r20m_path,
            image_path_12=self.band_12_r20m_path,
            save_location=f"{self.test_files_location}/indexes",
        )
        self.assertTrue(exists(save_location))

    def test_create_rgb_img(self):
        save_location = MetricsCalculator.create_rgb_img(
            sid_id=self.sid_id,
            blue_band_02=self.band_02_r20m_path,
            green_band_03=self.band_03_r20m_path,
            red_band_04=self.band_04_r20m_path,
            save_location=f"{self.test_files_location}/other",
        )
        self.assertTrue(exists(save_location))

    def test_calculate_true_color(self):
        save_location = MetricsCalculator.calculate_true_color(
            sid_id=self.sid_id,
            image_path_02=self.band_02_r20m_path,
            image_path_03=self.band_03_r20m_path,
            image_path_04=self.band_04_r20m_path,
            save_location=f"{self.test_files_location}/other",
        )
        self.assertTrue(exists(save_location))
