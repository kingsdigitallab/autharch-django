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
                if data is not None:
                    # Note - this is not ideal but is the most efficient way
                    if data.__class__.__name__ == 'ManyRelatedManager':
                        if data.count() > 0:
                            metadata.append({
                                "name": field.replace('_', ' ').title(),
                                "content": [str(item) for item in data.all()]
                            })
                    else:
                        if not data == '':
                            metadata.append({
                                "name": field.replace('_', ' ').title(),
                                "content": str(data)
                            })
        return metadata

    class Meta:
        model = ArchivalRecord
        metadata_fields = [
            'administrative_history', 'author', 'arrangement',
            'archival_level', 'cataloguer', 'creation_dates',
            'description', 'description_date', 'extent',
            'languages', 'notes', 'organisations_as_subjects',
            'persons_as_subjects', 'places_as_subjects',
            'publication_status', 'provenance', 'references',
            'related_materials', 'repository', 'rights_declaration',
            'subjects', 'title',
        ]
        exclude = ['polymorphic_ctype']
        depth = 10


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
