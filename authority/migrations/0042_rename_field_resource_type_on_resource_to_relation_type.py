# Generated by Django 2.1.3 on 2018-11-29 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0041_alter_place_fields_to_geonames_place'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resource',
            old_name='resource_type',
            new_name='relation_type',
        ),
    ]
