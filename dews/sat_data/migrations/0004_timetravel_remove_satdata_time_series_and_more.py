# Generated by Django 5.0 on 2023-12-19 13:32

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import utils.services.overwrite_storage
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sat_data', '0003_satdata_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeTravel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='No name', max_length=100, verbose_name='Name')),
                ('mission', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Mission')),
                ('thumbnail', models.ImageField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to='time_travel/<django.db.models.fields.CharField>/<django.db.models.fields.UUIDField>/thumbnail', verbose_name='Thumbnail')),
                ('coordinates', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Polygon Coordinates')),
                ('leaflet_coordinates', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Leaflet Coordinates')),
                ('product_type', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Product Type')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='satdata',
            name='time_series',
        ),
        migrations.AddField(
            model_name='satdata',
            name='time_travels',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sat_data', to='sat_data.timetravel'),
        ),
        migrations.DeleteModel(
            name='TimeSeries',
        ),
    ]
