import unittest

from backend.database.firebase import FirebaseDB
import firebase_admin
from backend.models.satellite_image_data import SatelliteImageData


class TestFirebaseDB(unittest.TestCase):
    fdb = None
    zip_file_path = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip"
    sid_id = ""

    @classmethod
    def setUpClass(cls):
        firebase_admin.initialize_app()
        cls.fdb = FirebaseDB(
            config_yml_path="test_config.yml",
            app_name="Test"
        )

    @classmethod
    def tearDownClass(cls):
        cls.fdb.clean_up()

    def test_create_sdi(self):
        sid = SatelliteImageData(
            zip_file_path=self.zip_file_path,
            calculate=False)
        self.sid_id = self.fdb.create_sdi(sid)
        self.assertNotEquals(self.sid_id, "")

    def test_get_sdi(self):
        sid = self.fdb.get_sdi(self.sid_id)
        self.assertIsNotNone(sid)
