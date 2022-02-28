# Generated by Django 4.0.2 on 2022-02-28 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("triggers", "0009_remove_trigger_recurring"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_friday",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_monday",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_saturday",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_sunday",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_thursday",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_tuesday",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="trigger",
            name="recur_on_wednesday",
            field=models.BooleanField(default=False),
        ),
    ]