# Generated by Django 3.1.12 on 2021-07-09 22:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eveuniverse", "0005_type_materials_and_sections"),
        ("structuretimers", "0003_auto_20210709_1204"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stagingsystem",
            name="eve_solar_system",
            field=models.OneToOneField(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_DEFAULT,
                related_name="+",
                to="eveuniverse.evesolarsystem",
            ),
        ),
    ]
