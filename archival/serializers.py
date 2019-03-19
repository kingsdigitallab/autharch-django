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

    class Meta:
        model = ArchivalRecord
        exclude = ['polymorphic_ctype']
        depth = 10


class CollectionSerializer(ArchivalRecordSerializer):
    class Meta(ArchivalRecordSerializer.Meta):
        model = Collection


class FileSerializer(ArchivalRecordSerializer):
    class Meta(ArchivalRecordSerializer.Meta):
        model = File


class ItemSerializer(ArchivalRecordSerializer):
    class Meta(ArchivalRecordSerializer.Meta):
        model = Item


class SeriesSerializer(ArchivalRecordSerializer):
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
