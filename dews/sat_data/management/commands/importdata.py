from io import BytesIO
import os
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpRequest, QueryDict
from django.middleware.csrf import get_token

from dews.settings import DB_USER
from sat_data.enums.sat_mission import SatMission
from sat_data.views import create_sat_data


class Command(BaseCommand):
    help = "Imports satellite data archives"

    def add_arguments(self, parser):
        parser.add_argument("source_path", type=str, help="Archive location")
        parser.add_argument("-m", "--mission", type=str,
                            help="[OPTIONAL] Dash seperated and lower case satellite mission of archive (e.g. 'sentinel-1a')")

    def handle(self, *args, **options):
        source_path: str = options.get("source_path")
        mission: str = options.get("mission")
        # Check mission
        if not mission:
            mission = SatMission.get_mission_by_filename(source_path)

        # Check if archive exists
        if not os.path.exists(source_path):
            raise CommandError(
                f"Archive does not exist. source_path='{source_path}'")

        # Create SatData object
        with open(source_path, "rb") as f:
            content = f.read()
        # Create request object
        request = HttpRequest()
        request.user = User.objects.get(username=DB_USER)
        request.method = "POST"
        request.path = "/sat_data/upload/" # TODO: check if ptional?!
        request.POST = QueryDict("", mutable=True)
        request.POST.update({
            "csrfmiddlewaretoken": get_token(request),
            "name": f"{os.path.basename(source_path)}",
        })
        archive = InMemoryUploadedFile(
            file=BytesIO(content),
            field_name='archive',
            name=os.path.basename(source_path),
            content_type='application/zip',
            size=len(content),
            charset=None
        )        
        request.FILES["archive"] = archive
        ok = create_sat_data(request, source_path)
        if not ok:
            raise CommandError(
                f"Failed to create SatData object. source_path='{source_path}'")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully imported archive. source_path='{source_path}'")
        )
