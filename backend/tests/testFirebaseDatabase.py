import unittest
from models.satellite_data.sentinel_2.sentinel2b_data import Sentinel2BData

from database.firebase import FirebaseApp, FirebaseDatabase


class TestFirebaseDB(unittest.TestCase):
    fdb = None
    zip_file_path = "/home/jtrvz/Documents/sid/S2B_MSIL2A_20230603T102559_N0509_R108_T32UPE_20230603T132937.zip"
    sid_id = ""
    app = None

    @classmethod
    def setUpClass(cls):
        cls.app = FirebaseApp.init_app()

    # @classmethod
    # def tearDownClass(cls):
    #     cls.app.clean_up()

    def test_create_entry(self):
        test = "Hello, World!"
        data = {
            "string": "Test",
            "stringInterpolation": f"I like to say '{test}!'",
            "int": 123,
            "bool": True,
            "double": 1.23,
        }
        ok = FirebaseDatabase.set_entry("test", data)
        self.assertTrue(ok)

    def test_create_sentinel2bdata(self):
        sid = Sentinel2BData(
            zip_file_path=self.zip_file_path,
            calculate=False)
        self.sid_id = self.fdb.create_sdi(sid)
        self.assertNotEquals(self.sid_id, "")

    def test_get_sentinel2bdata(self):
        sid = FirebaseDatabase.get_entry("sid/sentinel-2b", self.sid_id)
        self.assertIsNotNone(sid)
