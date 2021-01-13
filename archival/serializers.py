from authority.serializers import PlaceSerializer, RelatedEntitySerializer
from jargon.serializers import (
    PublicationStatusSerializer, ReferenceSourceSerializer,
    RepositorySerializer
)
from media.serializers import MediaPolymorphicSerializer
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (
    ArchivalRecord, ArchivalRecordImage, ArchivalRecordTranscription,
    Collection, File, Item, Reference, RelatedMaterialReference, Series)


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


class TranscriptionImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivalRecordImage
        fields = ['image', 'order']


class TranscriptionTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivalRecordTranscription
        fields = ['order', 'transcription']


class ArchivalRecordSerializer(serializers.ModelSerializer):
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

    def get_hierarchy(self, obj):
        ancestors = obj.get_ancestors()
        return self._serialise_ancestor(ancestors[-1], ancestors, obj)

    def get_languages(self, obj):
        return [language.label for language in obj.languages.all()]

    def get_origin_locations(self, obj):
        return [location.location for location in obj.origin_locations.all()]

    def _serialise_ancestor(self, ancestor, ancestors, selected_obj):
        data = {
            'pk': ancestor.pk,
            'is_selected': ancestor == selected_obj,
            'title': ancestor.title,
            'archival_level': ancestor.archival_level,
            'creation_dates': ancestor.creation_dates,
            'is_ancestor': ancestor in ancestors,
        }
        children = []
        children_desc = []
        if isinstance(ancestor, (Collection, Series)):
            series = list(ancestor.series_set.all().order_by(
                'calm_reference'))
            files = list(ancestor.file_set.all().order_by('calm_reference'))
            items = list(ancestor.item_set.all().order_by('calm_reference'))
            children = series + files + items
            if len(series) > 0:
                children_desc.append('{} series'.format(len(series)))
            if len(files) > 0:
                children_desc.append('{} files'.format(len(files)))
            if len(items) > 0:
                children_desc.append('{} items'.format(len(items)))
        elif isinstance(ancestor, File):
            files = list(ancestor.file_set.all().order_by('calm_reference'))
            items = list(ancestor.item_set.all().order_by('calm_reference'))
            children = files + items
            if len(files) > 0:
                children_desc.append('{} files'.format(len(files)))
            if len(items) > 0:
                children_desc.append('{} items'.format(len(items)))
        data['children'] = [
            self._serialise_ancestor(child, ancestors, selected_obj)
            for child in children]
        data['children_desc'] = '({})'.format(', '.join(children_desc))
        return data

    class Meta:
        model = ArchivalRecord
        fields = [
            'id', 'title', 'repository', 'description', 'references',
            'creation_dates', 'extent', 'languages', 'subjects',
            'places_as_subjects', 'persons_as_subjects', 'related_entities',
            'organisations_as_subjects', 'related_materials',
            'publication_status', 'media', 'persons_as_relations',
            'provenance', 'origin_locations', 'notes', 'rights_declaration'
        ]
        depth = 1


class CollectionSerializer(ArchivalRecordSerializer):
    hierarchy = serializers.SerializerMethodField()

    class Meta(ArchivalRecordSerializer.Meta):
        model = Collection
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['administrative_history', 'hierarchy']


class SeriesSerializer(ArchivalRecordSerializer):
    hierarchy = serializers.SerializerMethodField()

    class Meta(ArchivalRecordSerializer.Meta):
        model = Series
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['publications', 'hierarchy']


class FileSerializer(ArchivalRecordSerializer):
    creators = RelatedEntitySerializer(many=True, read_only=True)
    creation_places = PlaceSerializer(many=True, read_only=True)
    places_as_relations = PlaceSerializer(many=True, read_only=True)
    parent_collection = serializers.SerializerMethodField()
    transcriptions = TranscriptionTextSerializer(
        many=True, read_only=True, source='transcription_texts')
    media = TranscriptionImageSerializer(
        many=True, read_only=True, source='transcription_images')

    def get_parent_collection(self, obj):
        collection = obj.get_ancestors()[-1]
        return {'pk': collection.pk, 'title': collection.title}

    class Meta(ArchivalRecordSerializer.Meta):
        model = File
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['creators', 'creation_places', 'physical_description',
             'places_as_relations', 'url', 'withheld',
             'publication_permission', 'copyright_status', 'publications',
             'parent_collection', 'transcriptions', 'media']


class ItemSerializer(ArchivalRecordSerializer):
    creators = RelatedEntitySerializer(many=True, read_only=True)
    creation_places = PlaceSerializer(many=True, read_only=True)
    places_as_relations = PlaceSerializer(many=True, read_only=True)
    parent_collection = serializers.SerializerMethodField()
    transcriptions = TranscriptionTextSerializer(
        many=True, read_only=True, source='transcription_texts')
    media = TranscriptionImageSerializer(
        many=True, read_only=True, source='transcription_images')

    def get_parent_collection(self, obj):
        collection = obj.get_ancestors()[-1]
        return {'pk': collection.pk, 'title': collection.title}

    class Meta(ArchivalRecordSerializer.Meta):
        model = Item
        fields = ArchivalRecordSerializer.Meta.fields + \
            ['creators', 'creation_places', 'physical_description',
             'places_as_relations', 'url', 'withheld',
             'publication_permission', 'copyright_status', 'publications',
             'parent_collection', 'transcriptions', 'media']


class ArchivalRecordPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ArchivalRecord: ArchivalRecordSerializer,
        Collection: CollectionSerializer,
        Series: SeriesSerializer,
        File: FileSerializer,
        Item: ItemSerializer
    }
