# Generated by Django 2.2.13 on 2020-07-22 02:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archival', '0106_migrate_language_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivalrecord',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='record_control_languages', to='languages_plus.Language', verbose_name='Record language'),  # noqa
        ),
    ]
