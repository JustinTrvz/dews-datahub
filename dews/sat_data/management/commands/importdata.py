import os
import zipfile
from threading import Thread
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from sat_data.services.utils.file_utils import FileUtils
from sat_data.models import SatData, remove_media_root
from dews.sat_data.services.attr_adder import AttrAdder
from sat_data.enums.sat_mission import SatMission
from dews.settings import EXTRACTED_FILES_PATH, DB_USER


class Command(BaseCommand):
    help = "Imports satellite data archives"

    def add_arguments(self, parser):
        parser.add_argument("source_path", type=str, help="Archive location")
        parser.add_argument("-m", "--mission", type=str,
                            help="[OPTIONAL] Dash seperated and lower case satellite mission of archive (e.g. 'sentinel-1a')")

    def handle(self, *args, **options):
        source_path: str = options.get("source_path")
        mission: str = options.get("mission")

        # Check if archive exists
        if not os.path.exists(source_path):
            raise CommandError(
                f"Archive does not exist. source_path='{source_path}'")

        # Check mission
        if not mission:
            mission = SatMission.get_mission_by_filename(source_path)

        try:
            # Extract archive
            extracted_path = self.extract_archive(source_path, mission)
            # Create satellite data
            sat_data = SatData.create(source_path, mission, extracted_path)
            if sat_data is None:
                raise CommandError(
                    f"Failed to create SatData object. source_path='{source_path}', mission='{mission}'")
        except Exception as e:
            raise CommandError(
                f"Failed to extract archive. source_path='{source_path}', error='{e}'")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported archive. extracted_path='{extracted_path}', source_path='{source_path}'")
        )

    def extract_archive(self, source_path: str, mission: str):
        extracted_path = FileUtils.extract_archive(source_path, mission)

        # Check return value for error
        if extracted_path is None:
            raise CommandError(
                f"Failed to extract files from archive. source_path='{source_path}', extracted_path='{extracted_path}', mission='{mission}', error='{e}'")

        # Check if extracted dir exists
        if os.path.exists(extracted_path):
            return extracted_path
        else:
            raise CommandError(
                f"Directory at '{extracted_path}' does not exist.")
