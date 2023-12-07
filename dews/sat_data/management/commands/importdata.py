import os
import zipfile
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from sat_data.models import SatData
from sat_data.enums.satellite_mission import SatelliteMission
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
                f"Archive does not exist. source_path='{source_path}''")

        # Check mission input
        if not mission:
            source_path_splitted = source_path.split("/")
            # Search for mission in source_path
            for sat_mission in SatelliteMission.get_all():
                for path_elem in source_path_splitted:
                    if sat_mission == path_elem.lower():
                        mission = sat_mission

        if not mission:
            # If still no mission identified -> raise error
            raise CommandError(
                f"Could not identify satellite mission by source path. Please provide a mission using '-m'/'--mission'!")

        try:
            # Extract archive
            extracted_path = self.extract_archive(source_path, mission)
            # Create satellite data
            self.create_sat_data(source_path, mission, extracted_path)
        except Exception as e:
            raise CommandError(
                f"Failed to extract archive. source_path='{source_path}', error='{e}'")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported archive. extracted_path='{extracted_path}', source_path='{source_path}'")
        )

    def extract_archive(self, source_path: str, mission: str):
        try:
            with zipfile.ZipFile(source_path, "r") as zip_ref:
                folder_name, _ = os.path.splitext(os.path.basename(source_path))
                destination_path = os.path.join(EXTRACTED_FILES_PATH, mission)
                zip_ref.extractall(destination_path)
                extracted_path = os.path.join(destination_path, folder_name)
                self.stdout.write(f"Extracted archive from '{source_path}' to '{extracted_path}'.")
        except Exception as e:
            raise CommandError(f"Failed to extract files from archive. source_path='{source_path}', extracted_path='{extracted_path}', mission='{mission}', error='{e}'")

        if os.path.exists(extracted_path):
            return extracted_path
        else:
            raise CommandError(f"Directory at '{extracted_path}' does not exist.")

    def create_sat_data(self, source_path: str, mission: str, extracted_path: str):
        if not mission.lower() in [satellite_mission.value.lower() for satellite_mission in SatelliteMission]:
            raise CommandError(f"Mission '{mission}' is not a valid satellite mission! Please use e.g. 'sentinel-1a' or 'sentinel-2b'.")
        
        try:
            dews_user = User.objects.get(username="dews")

            # Create satellite data object
            sat_data = SatData(
                    mission=mission,
                    directory_path=extracted_path,
                    user=dews_user,
                )
            self.stdout.write("Created SatData object (not saved to database yet).")

            # Add mission and instrument specific attributes
            if mission == SatelliteMission.SENTINEL_1A.value:
                # Sentinel-1A
                metadata_path = os.path.join(extracted_path, "manifest.safe")
                sat_data.metadata.save("thumbnail.png", open(metadata_path, "rb"))
                self.stdout.write("Added metadata.")
                thumbnail_path = os.path.join(extracted_path, "preview", "thumbnail.png")
                sat_data.thumbnail.save("manifest.safe", open(thumbnail_path, "rb"))
                self.stdout.write("Added thumbnail.")
            else:
                # All other satellite missions
                self.stdout.write(f"No additional attributes added.")
                sat_data.save()

            # Calculations
            # TODO: calculate

            self.stdout.write(f"Saved SatData object to database.")
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully created a SatData object. directory_path='{extracted_path}', user_id='{DB_USER}', mission='{mission}'")
            )
            return True
        except Exception as e:
            raise CommandError(f"Failed to create SatData object. error='{e}', source_path='{source_path}', mission='{mission}'")
