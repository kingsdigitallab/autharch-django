# Generated by Django 2.1.7 on 2019-05-07 14:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authority', '0055_add_identity_rel'),
    ]

    def forward_operation(apps, schema_editor):
        Description = apps.get_model('authority', 'Description')
        Relation = apps.get_model('authority', 'Relation')
        Resource = apps.get_model('authority', 'Resource')

        for obj in Description.objects.all():
            identity = obj.entity.identities.order_by(
                '-preferred_identity').first()
            obj.identity = identity
            obj.save()

        for obj in Relation.objects.all():
            identity = obj.entity.identities.order_by(
                '-preferred_identity').first()
            obj.identity = identity
            obj.save()

        for obj in Resource.objects.all():
            identity = obj.entity.identities.order_by(
                '-preferred_identity').first()
            obj.identity = identity
            obj.save()
    
    def reverse_operation(apps, schema_editor):
        Description = apps.get_model('authority', 'Description')
        Relation = apps.get_model('authority', 'Relation')
        Resource = apps.get_model('authority', 'Resource')

        for obj in Description.objects.all():
            obj.identity = None
            obj.save()

        for obj in Relation.objects.all():
            obj.identity = None
            obj.save()

        for obj in Resource.objects.all():
            obj.identity = None
            obj.save()

    operations = [
        migrations.RunPython(forward_operation, reverse_operation)
    ]
