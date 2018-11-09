# Generated by Django 2.1.3 on 2018-11-09 16:51

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('jargon', '0009_entityrelationtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(max_length=128, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
