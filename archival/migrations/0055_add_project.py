# Generated by Django 2.1.7 on 2019-06-18 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archival', '0054_add_creation_places_to_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True)),
            ],
        ),
    ]
