import unittest
from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData

from database.firebase import FirebaseApp, FirebaseStorage
from backend.config import *
from os.path import exists


class TestFirebaseStorage(unittest.TestCase):
    img_path = ROOT_PATH + "/tests/data/test.png"
    img_name = img_path.split("/")[-1]
    sid_id = ""
    app = None

    @classmethod
    def setUpClass(cls):
        cls.app = FirebaseApp.init_app()

    # @classmethod
    # def tearDownClass(cls):
    #     cls.app.clean_up()

    def test_upload_file(self):
        # Upload file
        print(f"IMGPATH: {self.img_path}")
        storage_path = FirebaseStorage.upload_file("test", self.img_path)
        self.assertEqual(storage_path, "")
        # File existance check
        file_exists = FirebaseStorage.file_exists("test", self.img_name)
        self.assertTrue(file_exists)

    def test_get_file(self):
        local_path = FirebaseStorage.download_file(f"test/{self.img_name}")
        file_exists = exists(local_path)
        self.assertTrue(file_exists)
