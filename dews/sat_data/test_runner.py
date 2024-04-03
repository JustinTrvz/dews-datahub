from django.test.runner import DiscoverRunner
from django.db import connection

class PostGISTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        # Set up the test databases
        result = super().setup_databases(**kwargs)
        # Add the PostGIS extensions
        with connection.cursor() as cursor:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
            cursor.execute('CREATE EXTENSION IF NOT EXISTS postgis_raster;')
        return result
