from authority.serializers import PlaceSerializer, RelatedEntitySerializer
from jargon.serializers import (
    PublicationStatusSerializer, ReferenceSourceSerializer,
    RepositorySerializer
)
from media.serializers import MediaPolymorphicSerializer
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (
    ArchivalRecord, Collection, File, Item, Reference,
    RelatedMaterialReference, Series)


class ReferenceSerializer(serializers.ModelSerializer):
    source = ReferenceSourceSerializer(many=False, read_only=True)

    class Meta:
        model = Reference
        fields = '__all__'
        depth = 10


class RelatedRecordSerializer(serializers.ModelSerializer):
    resourcetype = serializers.SerializerMethodField(read_only=True)

    def get_resourcetype(self, obj):
        return obj.related_record.archival_level

    class Meta:
        model = RelatedMaterialReference
        exclude = ['id', 'record']


class ArchivalRecordSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='archivalrecord-detail', lookup_field='pk'
    )

    media = MediaPolymorphicSerializer(many=True, read_only=True)
    publication_status = PublicationStatusSerializer(
        many=False, read_only=True)
    references = ReferenceSerializer(many=True, read_only=True)
    repository = RepositorySerializer(many=False, read_only=True)
    languages = serializers.SerializerMethodField()
    organisations_as_subjects = RelatedEntitySerializer(
        many=True, read_only=True)
    persons_as_subjects = RelatedEntitySerializer(many=True, read_only=True)
    places_as_subjects = PlaceSerializer(many=True, read_only=True)
    related_entities = RelatedEntitySerializer(many=True, read_only=True)
    related_materials = RelatedRecordSerializer(
        many=True, read_only=True, source='referenced_related_materials')
    persons_as_relations = RelatedEntitySerializer(many=True, read_only=True)
    origin_locations = serializers.SerializerMethodField()

    def get_languages(self, obj):
        return [language.label for language in obj.languages.all()]

    def get_origin_locations(self, obj):
        return [location.location for location in obj.origin_locations.all()]

    class Meta:
        model = ArchivalRecord
        fields = [
            'url', 'id', 'title', 'repository', 'description', 'references',
            'creation_dates', 'extent', 'languages', 'subjects',
            'places_as_subjects', 'persons_as_subjects', 'related_entities',
            'organisations_as_subjects', 'related_materials',
            'publication_status', 'media', 'persons_as_relations',
            'provenance', 'origin_locations', 'notes', 'rights_declaration'
        ]
        depth = 1


class CollectionSerializer(ArchivalRecordSerializer):
    series_set = ArchivalRecordSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = Collection
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['administrative_history', 'series_set']


class FileSerializer(ArchivalRecordSerializer):
    creators = RelatedEntitySerializer(many=True, read_only=True)
    file_set = ArchivalRecordSerializer(many=True, read_only=True)
    item_set = ArchivalRecordSerializer(many=True, read_only=True)
    creation_places = PlaceSerializer(many=True, read_only=True)
    places_as_relations = PlaceSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = File
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['file_set', 'item_set', 'creators', 'creation_places',
             'physical_description', 'places_as_relations', 'url', 'withheld',
             'publication_permission', 'copyright_status']


class ItemSerializer(ArchivalRecordSerializer):
    creation_places = PlaceSerializer(many=True, read_only=True)
    places_as_relations = PlaceSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = Item
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['creators', 'creation_places', 'physical_description',
             'places_as_relations', 'url', 'withheld',
             'publication_permission', 'copyright_status']


class SeriesSerializer(ArchivalRecordSerializer):
    series_set = ArchivalRecordSerializer(many=True, read_only=True)
    file_set = ArchivalRecordSerializer(many=True, read_only=True)
    item_set = ArchivalRecordSerializer(many=True, read_only=True)

    class Meta(ArchivalRecordSerializer.Meta):
        model = Series
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['file_set', 'item_set', 'series_set']


class ArchivalRecordPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ArchivalRecord: ArchivalRecordSerializer,
        Collection: CollectionSerializer,
        Series: SeriesSerializer,
        File: FileSerializer,
        Item: ItemSerializer
    }
