# Generated by Django 2.2.13 on 2020-09-08 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archival', '0115_migrate_calm_references'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivalrecord',
            name='calm_reference',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True, verbose_name='CALM reference'),
        ),
    ]
