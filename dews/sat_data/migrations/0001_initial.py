# Generated by Django 5.0 on 2023-12-10 10:50

import django.db.models.deletion
import sat_data.enums.sat_mission
import sat_data.models
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
                ('name', models.CharField(default='No name', max_length=100, verbose_name='Name')),
                ('mission', models.CharField(blank=True, choices=sat_data.enums.sat_mission.SatMission.as_dict, default='unknown', max_length=50, verbose_name='Mission')),
                ('product_type', models.CharField(blank=True, default='unknown', max_length=50, verbose_name='Product Type')),
                ('directory_path', models.CharField(blank=True, max_length=255, verbose_name='Directory Path')),
                ('archive', models.FileField(max_length=255, upload_to=sat_data.models.archive_upload_path, verbose_name='Archive')),
                ('metadata', models.FileField(blank=True, max_length=255, null=True, upload_to=sat_data.models.metadata_upload_path, verbose_name='Metadata')),
                ('thumbnail', models.ImageField(blank=True, max_length=255, null=True, upload_to=sat_data.models.thumbnail_upload_path, verbose_name='Thumbnail')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, default=sat_data.models.get_dews_user, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sat_data',
                'ordering': ['creation_time'],
            },
        ),
        migrations.CreateModel(
            name='ImageInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_type', models.CharField(max_length=20)),
                ('img_path', models.CharField(max_length=255)),
                ('archived_img_paths', models.TextField()),
                ('sat_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sat_data.satdata')),
            ],
            options={
                'db_table': 'image_info',
            },
        ),
        migrations.CreateModel(
            name='CaptureInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_start_time', models.DateTimeField()),
                ('product_stop_time', models.DateTimeField()),
                ('product_type', models.CharField(max_length=50)),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='capture_info', to='sat_data.satdata')),
            ],
            options={
                'db_table': 'capture_info',
            },
        ),
        migrations.CreateModel(
            name='Calculation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('sat_data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sat_data.satdata')),
            ],
            options={
                'db_table': 'calculation',
            },
        ),
        migrations.CreateModel(
            name='BoundLatitudes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('north', models.FloatField()),
                ('east', models.FloatField()),
                ('south', models.FloatField()),
                ('west', models.FloatField()),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='bound_latitudes', to='sat_data.satdata')),
            ],
            options={
                'db_table': 'bound_latitudes',
            },
        ),
        migrations.CreateModel(
            name='BandInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('range', models.IntegerField(choices=[(10, '10'), (20, '20'), (60, '60')], default=10, help_text='One pixel in meter')),
                ('aot_path', models.CharField(blank=True, max_length=255, null=True)),
                ('scl_path', models.CharField(blank=True, max_length=255, null=True)),
                ('tci_path', models.CharField(blank=True, max_length=255, null=True)),
                ('wvp_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b01_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b02_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b03_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b04_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b05_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b06_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b07_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b08_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b8a_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b09_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b10_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b11_path', models.CharField(blank=True, max_length=255, null=True)),
                ('b12_path', models.CharField(blank=True, max_length=255, null=True)),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='band_info', to='sat_data.satdata')),
            ],
            options={
                'db_table': 'band_info',
            },
        ),
        migrations.CreateModel(
            name='AreaInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('postal_code', models.CharField(max_length=20)),
                ('capture_time', models.DateTimeField(null=True)),
                ('sat_data', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='area_info', to='sat_data.satdata')),
            ],
            options={
                'db_table': 'area_info',
            },
        ),
    ]
