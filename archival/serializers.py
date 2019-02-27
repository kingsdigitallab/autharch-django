from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import ArchivalRecord, Collection, File, Item, Series, Reference


def get_field_names(model, exclude=[]):
    fields = list(map(lambda x: x.name, model._meta.get_fields()))
    return list(filter(lambda x: x not in exclude, fields))


class ArchivalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivalRecord
        fields = ['title']


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Collection
        exclude = ['polymorphic_ctype']
        depth = 10


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ReferenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'
        depth = 2


class SeriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = '__all__'


class ArchivalRecordPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        ArchivalRecord: ArchivalRecordSerializer,
        Collection: CollectionSerializer,
        Series: SeriesSerializer,
        File: FileSerializer,
        Item: ItemSerializer
    }
