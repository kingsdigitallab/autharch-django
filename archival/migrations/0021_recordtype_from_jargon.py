# Generated by Django 2.1.3 on 2018-11-09 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jargon', '0004_recordtype'),
        ('archival', '0020_delete_model_recordtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='record_type',
            field=models.ManyToManyField(to='jargon.RecordType'),
        ),
        migrations.AddField(
            model_name='item',
            name='record_type',
            field=models.ManyToManyField(to='jargon.RecordType'),
        ),
    ]
