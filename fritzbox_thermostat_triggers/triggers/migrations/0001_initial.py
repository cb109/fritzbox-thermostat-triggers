# Generated by Django 4.0.2 on 2022-02-27 11:10

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Thermostat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("ain", models.CharField(max_length=64)),
                ("name", models.CharField(max_length=128)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Trigger",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("time", models.DateTimeField()),
                (
                    "temperature",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(28.0),
                        ]
                    ),
                ),
                ("triggered", models.BooleanField(default=False)),
                (
                    "thermostat",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="triggers.thermostat",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
