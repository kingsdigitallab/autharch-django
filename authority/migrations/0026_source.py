# Generated by Django 2.0.9 on 2018-11-06 12:16

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0025_change_meta_options_on_control'),
    ]

    operations = [
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=256)),
                ('url', models.URLField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('control', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authority.Control')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
