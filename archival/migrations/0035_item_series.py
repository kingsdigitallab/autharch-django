# Generated by Django 2.1.3 on 2018-12-05 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('archival', '0034_alter_field_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='archival.Series'),
        ),
    ]
