import uuid
from django.test import TestCase
from sat_data.services.utils.file_utils import FileUtils
from sat_data.services.metrics_calc import MetricsCalculator
from sat_data.enums.sat_mission import SatMission
from sat_data.services.attr_adder import AttrAdder
from sat_data.models import Band, SatData, remove_media_root
from django.contrib.auth.models import User


class FileUtilsTestCase(TestCase):
    manifest_path = "/dews/media/sat_data/extracted/sentinel-2b/S2B_MSIL2A_20231213T104339_N0510_R008_T32UNE_20231213T122711.SAFE/manifest.safe"

    def test_split_tiff(self):
        pass  # TODO: implement

    def test_extract_tar(self):
        pass  # TODO: implement

    def test_extract_archive(self):
        pass  # TODO: implement

    def test_generate_path(self):
        pass  # TODO: implement

    def test_xml_to_dict(self):
        xml_dict = FileUtils.xml_to_dict(self.manifest_path)

        self.assertEqual(
            xml_dict['xfdu:XFDU']['@version'],
            "esa/safe/sentinel/1.1/sentinel-2/msi/archive_l2a_user_product",
        )
        self.assertEqual(
            xml_dict['xfdu:XFDU']['informationPackageMap']['xfdu:contentUnit']['@textInfo'],
            "SENTINEL-2 MSI Level-2A User Product",
        )

    def test_get_dict_value_by_key(self):
        xml_dict = FileUtils.xml_to_dict(self.manifest_path)
        coordinates = FileUtils.get_all_dict_values_by_key(xml_dict, "gml:coordinates")
        self.assertEqual(
            coordinates,
            ["54.13844097161835 10.38459330562137 54.030215436026005 10.321913512155875 53.88700515510197 10.23955571254994 53.743738142208336 10.15732241658233 53.60037956097424 10.075596550240888 53.45700618416768 9.994234233126434 53.31360123538213 9.913291721709566 53.17015021270508 9.832938769806916 53.1554879366226 9.824809627989502 53.16117354480671 8.999700868340735 54.148104103961266 8.99969379936479 54.13844097161835 10.38459330562137"]
        )

    def test_get_all_dict_values_by_key(self):
        pass  # TODO: implement


class SatDataTestCase(TestCase):
    # Archive
    sat_data: SatData = None  # will be overwritten
    extracted_path: str = "sat_data/extracted/sentinel-2b/S2B_MSIL2A_20231213T104339_N0510_R008_T32UNE_20231213T122711.SAFE"
    archive_path: str = "/dews/media/sat_data/archive/sentinel-2b/S2B_MSIL2A_20231213T104339_N0510_R008_T32UNE_20231213T122711.SAFE.zip"
    # Sentinel Hub API
    sat_data_sh: SatData = None  # will be overwritten
    extracted_path_sh: str = "sentinel_hub/1f8845535b28b8ea81dbb1cf63b15974"
    # User object
    testuser: User = None  # will be overwritten
    # SatData dict
    sat_data_dict = {
        "archive": sat_data,
        "api": sat_data_sh,
    }

    def setUp(self) -> None:
        # Create test user
        self.testuser = User.objects.create_user(
            username='testuser', password='test')
        print(f"Created user '{self.testuser.username}' for testing.")

        # Archive
        self.sat_data = SatData.objects.create(
            id=uuid.uuid4(),
            user=self.testuser,
            archive=self.archive_path,
        )
        self.sat_data.save()
        print("Created SatData object for testing (archive).")

        # SH API
        self.sat_data_sh = SatData.objects.create(
            id=uuid.uuid4(),
            user=self.testuser,
        )
        self.sat_data.save()
        print("Created SatData object for testing (SH API).")

    def test_attr_adder(self):
        """
        Test the class AttrAdder with a SatData object that was created using an archive.
        """
        sat_data = self.sat_data
        attr_adder = AttrAdder(
            sat_data=self.sat_data,
            extracted_path=self.extracted_path,
            mission=SatMission.SENTINEL_2B.value,
        )
        print("Created AttrAdder object for testing (archive).")
        attr_adder.start()
        print("Bands count: ", sat_data.bands.count())

        # Product type
        self.assertIsNotNone(sat_data.product_type)
        # Extracted path
        self.assertEqual(sat_data.extracted_path,
                         remove_media_root(self.extracted_path))
        # Mission
        self.assertEqual(sat_data.mission,
                         SatMission.SENTINEL_2B.value)
        # Name
        self.assertIsNotNone(sat_data.name)
        # Coordinates
        self.assertIsNotNone(sat_data.coordinates)
        self.assertIsNotNone(sat_data.leaflet_coordinates)
        # TimeTravels
        self.assertIsNotNone(sat_data.time_travels)
        # TODO: check if Band objects were created

    def test_attr_adder_sh(self):
        """
        Test the class AttrAdder with a SatData object that was created using the Sentinel Hub API.
        """
        sat_data = self.sat_data_sh
        bbox = (12.44693, 41.870072, 12.541001, 41.917096)
        bands = ["B02", "B03", "B04", "B08"]
        attr_adder_sh = AttrAdder(
            sat_data=sat_data,
            extracted_path=self.extracted_path_sh,
            mission=SatMission.SENTINEL_2B.value,
            sh_request=True,
            bbox=bbox,
            bands=bands,
        )
        print("Created AttrAdder object for testing (SH API).")
        attr_adder_sh.start()
        print("Bands count: ", sat_data.bands.count())
        print(sat_data.bands.all())

        # Product type
        self.assertIsNotNone(sat_data.product_type)
        # Extracted path
        self.assertEqual(sat_data.extracted_path,
                         self.extracted_path_sh)
        # Mission
        self.assertEqual(sat_data.mission,
                         SatMission.SENTINEL_2B.value)
        # Name
        self.assertIsNotNone(sat_data.name)
        # Thumbnail (request always returns a thumbnail)
        self.assertIsNotNone(sat_data.thumbnail)
        # Coordinates
        self.assertIsNotNone(sat_data.coordinates)
        self.assertIsNotNone(sat_data.leaflet_coordinates)
        # TimeTravels
        self.assertIsNotNone(sat_data.time_travels)
        # TODO: check if Band objects were created
        # Number of Band objects
        self.assertEqual(len(bands), sat_data.bands.count())

    def test_ndvi(self):
        # NDVI Index object should not exist
        for create_mod, sat_data in self.sat_data_dict.items():
            print(
                f"Create mode is '{create_mod}'. sat_data.id='{sat_data.id}'.")
            ndvi_idx = sat_data.index.filter(idx_type="ndvi").first()
            self.assertIsNone(ndvi_idx)
            mc = MetricsCalculator(
                sat_data=sat_data,
                metrics_to_calc=["ndvi"],
            )
            print("Created MetricsCalculator object for testing (NDVI).")
            mc.start()
            print("MetricsCalculator object started for testing (NDVI).")
            # NDVI Index object should exist
            ndvi_idx = sat_data.index.filter(idx_type="ndvi").first()
            self.assertIsNotNone(ndvi_idx)

    def test_rgb(self):
        # RGB Index object should not exist
        for create_mod, sat_data in self.sat_data_dict.items():
            print(
                f"Create mode is '{create_mod}'. sat_data.id='{sat_data.id}'.")
            rgb_idx = sat_data.index.filter(idx_type="rgb").first()
            self.assertIsNone(rgb_idx)
            mc = MetricsCalculator(
                sat_data=sat_data,
                metrics_to_calc=["rgb"],
            )
            print("Created MetricsCalculator object for testing (RGB).")
            mc.start()
            print("MetricsCalculator object started for testing (RGB).")
            # RGB Index object should exist
            rgb_idx = sat_data.index.filter(idx_type="rgb").first()
            self.assertIsNotNone(rgb_idx)
