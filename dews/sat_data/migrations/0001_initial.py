# Generated by Django 5.0 on 2023-12-19 09:40

import django.contrib.gis.db.models.fields
import django.db.models.deletion
import sat_data.models
import utils.services.overwrite_storage
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SatData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('mission', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Mission')),
                ('product_type', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Product Type')),
                ('extracted_path', models.CharField(blank=True, max_length=255, verbose_name='Extracted Path')),
                ('archive', models.FileField(max_length=255, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.archive_upload_path, verbose_name='Archive')),
                ('name', models.CharField(blank=True, default='<django.db.models.fields.files.FileField>', max_length=100, verbose_name='Name')),
                ('manifest', models.FileField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.metadata_upload_path, verbose_name='Manifest')),
                ('eop_metadata', models.FileField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.metadata_upload_path, verbose_name='EOP Metadata')),
                ('xfdu_manifest', models.FileField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.metadata_upload_path, verbose_name='Xfdu Manifest')),
                ('inspire', models.FileField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.metadata_upload_path, verbose_name='Inspire')),
                ('thumbnail', models.ImageField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.thumbnail_upload_path, verbose_name='Thumbnail')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('coordinates', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Polygon Coordinates')),
                ('leaflet_coordinates', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Leaflet Coordinates')),
                ('user', models.ForeignKey(blank=True, default=sat_data.models.get_dews_user, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sat_data',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='TimeSeries',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='No name', max_length=100, verbose_name='Name')),
                ('mission', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Mission')),
                ('thumbnail', models.ImageField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to='time_series/<django.db.models.fields.CharField>/<django.db.models.fields.UUIDField>/thumbnail', verbose_name='Thumbnail')),
                ('coordinates', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Polygon Coordinates')),
                ('leaflet_coordinates', django.contrib.gis.db.models.fields.PolygonField(blank=True, null=True, srid=4326, verbose_name='Leaflet Coordinates')),
                ('product_type', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Product Type')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('stop_time', models.DateTimeField(blank=True, null=True)),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='area_info', serialize=False, to='sat_data.satdata')),
            ],
            options={
                'db_table': 'area_info',
            },
        ),
        migrations.CreateModel(
            name='BandInfo',
            fields=[
                ('range', models.IntegerField(blank=True, choices=[(10, '10'), (20, '20'), (60, '60')], default=10, help_text='One pixel in meter')),
                ('aot', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='AOT')),
                ('scl', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='SCL')),
                ('tci', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='TCI')),
                ('wvp', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='WVP')),
                ('b01', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B01')),
                ('b02', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B02')),
                ('b03', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B03')),
                ('b04', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B04')),
                ('b05', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B05')),
                ('b06', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B06')),
                ('b07', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B0')),
                ('b08', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B07')),
                ('b8a', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B8A')),
                ('b09', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B09')),
                ('b10', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B10')),
                ('b11', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B11')),
                ('b12', models.ImageField(blank=True, default='None', max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.band_upload_path, verbose_name='B12')),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='band_info', serialize=False, to='sat_data.satdata')),
            ],
            options={
                'db_table': 'band_info',
            },
        ),
        migrations.CreateModel(
            name='CaptureInfo',
            fields=[
                ('product_start_time', models.DateTimeField()),
                ('product_stop_time', models.DateTimeField()),
                ('product_type', models.CharField(max_length=50)),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='capture_info', serialize=False, to='sat_data.satdata')),
            ],
            options={
                'db_table': 'capture_info',
            },
        ),
        migrations.CreateModel(
            name='IndexInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idx_type', models.CharField(max_length=20)),
                ('img', models.ImageField(blank=True, max_length=255, null=True, storage=utils.services.overwrite_storage.OverwriteStorage(), upload_to=sat_data.models.index_upload_path, verbose_name='Index img')),
                ('archived_img_paths', models.TextField()),
                ('sat_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sat_data.satdata')),
            ],
            options={
                'db_table': 'index_info',
            },
        ),
        migrations.AddField(
            model_name='satdata',
            name='time_series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sat_data', to='sat_data.timeseries'),
        ),
    ]
