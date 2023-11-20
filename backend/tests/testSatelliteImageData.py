import unittest

from backend.models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData



class TestSatelliteImageData(unittest.TestCase):
    zip_file_path = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip"
    test_files_location = "/home/jtrvz/Git/remote_sensing_analysis/moisture_detector/test_files"

    def test_init_no_calc(self):
        sid = Sentinel2BData(
            zip_file_path=self.zip_file_path,
            calculate=False
        )
        self.assertIsNotNone(sid)

        # The following check will be executed in the init function but still we can check one more time
        self.assertTrue(sid.is_valid() == 1)

    def test_init_with_calc(self):
        sid = Sentinel2BData(
            zip_file_path=self.zip_file_path,
            img_save_location=f"{self.test_files_location}"
        )  # default value of 'calculate' is True
        self.assertIsNotNone(sid)

        # The following check will be executed in the init function but still we can check one more time
        self.assertTrue(sid.is_valid() == 1)
