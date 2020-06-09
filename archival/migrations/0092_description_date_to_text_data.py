# Generated by Django 2.2.12 on 2020-06-09 01:04

from django.db import migrations


def date_to_iso_string(apps, schema_editor):
    # We can't import the models directly as each may be a newer
    # version than this migration expects. We use the historical
    # version.
    ArchivalRecord = apps.get_model('archival', 'ArchivalRecord')
    for record in ArchivalRecord.objects.all():
        record.description_date_text = record.description_date.isoformat()
        record.save()


class Migration(migrations.Migration):

    dependencies = [
        ('archival', '0091_archivalrecord_description_date_text'),
    ]

    operations = [
        migrations.RunPython(date_to_iso_string),
    ]
