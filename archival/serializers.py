from authority.serializers import EntitySerializer
from jargon.serializers import (
    PublicationStatusSerializer, ReferenceSourceSerializer,
    RepositorySerializer
)
from media.serializers import MediaPolymorphicSerializer
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import ArchivalRecord, Collection, File, Item, Reference, Series


class ReferenceSerializer(serializers.ModelSerializer):
    source = ReferenceSourceSerializer(many=False, read_only=True)

    class Meta:
        model = Reference
        fields = '__all__'
        depth = 10


class ArchivalRecordSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='archivalrecord-detail', lookup_field='pk'
    )

    media = MediaPolymorphicSerializer(many=True, read_only=True)
    publication_status = PublicationStatusSerializer(
        many=False, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    repository = RepositorySerializer(many=False, read_only=True)
    creators = EntitySerializer(many=True, read_only=True)

    metadata = serializers.SerializerMethodField()

    def get_metadata(self, obj):
        metadata = []

        for field in self.Meta.metadata_fields:
            if hasattr(obj, field):
                data = getattr(obj, field)
                if data:
                    # Note - this is not ideal but is the most efficient way
                    if data.__class__.__name__ == 'ManyRelatedManager':
                        if data.count() > 0:
                            items = data.all()

                            metadata.append({
                                'name': field.replace('_', ' '),
                                'content': [str(item) for item in items],
                                'items': [
                                    {
                                        'id': item.pk,
                                        'type':
                                        item.__class__.__name__.lower(),
                                        'value': str(item)
                                    }
                                    for item in items
                                ]
                            })
                    else:
                        if data:
                            metadata.append({
                                'name': field.replace('_', ' '),
                                'content': str(data)
                            })

        return metadata

    class Meta:
        model = ArchivalRecord
        metadata_fields = [
            'title', 'archival_level', 'author', 'creation_dates',
            'references', 'persons_as_relations',
            'places_as_relations', 'description', 'languages', 'extent',
            'physical_description', 'record_type', 'provenance',
            'administrative_history', 'notes',
            'arrangement', 'subjects', 'persons_as_subjects',
            'organisations_as_subjects',
            'places_as_subjects', 'publication_permission', 'withheld',
            'related_materials', 'publications', 'url', 'rights_declaration'
        ]
        exclude = ['polymorphic_ctype']
        depth = 1


class CollectionSerializer(ArchivalRecordSerializer):
    series_set = ArchivalRecordSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = Collection


class FileSerializer(ArchivalRecordSerializer):
    file_set = ArchivalRecordSerializer(many=True, read_only=True)
    item_set = ArchivalRecordSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = File


class ItemSerializer(ArchivalRecordSerializer):
    class Meta(ArchivalRecordSerializer.Meta):
        model = Item


class SeriesSerializer(ArchivalRecordSerializer):
    series_set = ArchivalRecordSerializer(many=True, read_only=True)
    file_set = ArchivalRecordSerializer(many=True, read_only=True)
    item_set = ArchivalRecordSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = Series


class ArchivalRecordPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ArchivalRecord: ArchivalRecordSerializer,
        Collection: CollectionSerializer,
        Series: SeriesSerializer,
        File: FileSerializer,
        Item: ItemSerializer
    }
