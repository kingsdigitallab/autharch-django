# Generated by Django 2.1.3 on 2018-12-03 11:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jargon', '0014_repository'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='repository',
            unique_together={('code', 'title')},
        ),
    ]
