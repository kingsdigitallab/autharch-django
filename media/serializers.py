
from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import File, Image, Media


class MediaSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='media-detail', lookup_field='pk'
    )

    class Meta:
        model = Media
        exclude = ['polymorphic_ctype']
        depth = 1


class FileSerializer(MediaSerializer):
    class Meta(MediaSerializer.Meta):
        model = File


class ImageSerializer(MediaSerializer):
    class Meta(MediaSerializer.Meta):
        model = Image


class MediaPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Media: MediaSerializer,
        File: FileSerializer,
        Image: ImageSerializer
    }
