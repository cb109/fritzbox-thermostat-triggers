# Generated by Django 4.0.2 on 2022-02-28 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("triggers", "0004_trigger_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="trigger",
            old_name="triggered",
            new_name="enabled",
        ),
    ]