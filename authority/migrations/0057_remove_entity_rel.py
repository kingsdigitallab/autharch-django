# Generated by Django 2.1.7 on 2019-05-07 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0056_convert_entity_rels_to_identity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='description',
            name='entity',
        ),
        migrations.RemoveField(
            model_name='relation',
            name='entity',
        ),
        migrations.RemoveField(
            model_name='resource',
            name='entity',
        ),
        migrations.AlterField(
            model_name='description',
            name='identity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descriptions', to='authority.Identity'),
        ),
        migrations.AlterField(
            model_name='relation',
            name='identity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='authority.Identity'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='identity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='authority.Identity'),
        ),
    ]
