# Generated by Django 5.0 on 2023-12-19 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sat_data', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='satdata',
            name='name',
        ),
    ]